import asyncio
import logging
import nats.aio.client
import json
from nats.aio.errors import ErrNoServers, ErrConnectionClosed
from datetime import datetime

logging.basicConfig(
    format=u'%(levelname)-8s [%(asctime)s]  %(message)s',
    level=logging.INFO
)


class scanner_wrapper:
    config = {
        # Count packets from queue received at a time
        # "data_pack_size": 1,
        "send_meta": True,
        "send_raw": False,
    }

    def __init__(self, **kwargs):
        if "name" in kwargs:
            nats.aio.client.__version__ = kwargs["name"]
        else:
            raise Exception("No name for module")
        self.config.update(kwargs)

    def configure(self, **kwargs):
        self.config.update(kwargs)

    async def _run(self, loop, func):
        nc = nats.aio.client.Client()

        @asyncio.coroutine
        def disconnected_cb():
            logging.info("Got disconnected!")

        @asyncio.coroutine
        def reconnected_cb():
            # See who we are connected to on reconnect.
            logging.info("Got reconnected to " + str(nc.connected_url.netloc))

        @asyncio.coroutine
        def error_cb(e):
            logging.error("There was an error: " + str(e))

        @asyncio.coroutine
        def closed_cb():
            logging.info("Connection is closed")

        # Configuring nats
        options = {
            # Setup pool of servers from a NATS cluster.
            "servers": self.config['nats'],
            "io_loop": loop,
            # Will try to connect to servers in order of configuration,
            # by defaults it connect to one in the pool randomly.
            "dont_randomize": True,
            # Optionally set reconnect wait and max reconnect attempts.
            # This example means 10 seconds total per backend.
            "max_reconnect_attempts": 5,
            "reconnect_time_wait": 10,
            # Setup callbacks to be notified on disconnects and reconnects
            "disconnected_cb": disconnected_cb,
            "reconnected_cb": reconnected_cb,
            # Setup callbacks to be notified when there is an error
            # or connection is closed.
            "error_cb": error_cb,
            "closed_cb": closed_cb
        }

        while not nc.is_connected:
            try:
                await nc.connect(**options)
                logging.info("Connected to NATS.")
                logging.info("Started module named '{name}'.".format(
                    name=self.config["name"]))
            except ErrNoServers as e:
                # Could not connect to any server in the cluster.
                logging.error(e)

        @asyncio.coroutine
        async def message_handler(msg):
            cur_pipeline = msg.subject
            task_raw = msg.data.decode()
            status = ""
            new_pipeline = ".".join(cur_pipeline.split(".")[1:])
            logging.info("Received from '{cur_pipeline}': {task}".format(
                cur_pipeline=cur_pipeline, task=task_raw))
            try:
                task = json.loads(task_raw)
                data, meta = task["data"], task["meta"]

                logging.info("Starting '{name}'".format(
                    name=self.config["name"]))
                try:
                    # Scanning (start function)
                    result = func(cur_pipeline, data, meta)
                except Exception as e:
                    status = "func_error"
                    raise Exception("Error in worker function: " + str(e))
                if result:
                    if new_pipeline:
                        try:
                            status = "ok"
                            for res in result:
                                if not self.config["send_raw"]:
                                    res = json.dumps(
                                        {"data": res, "meta": meta}).encode()

                                await nc.publish(new_pipeline, res)
                                logging.info("Result: {result} \n Was sent to '{pipeline}'".format(
                                    result=res, pipeline=new_pipeline))
                        except ErrConnectionClosed:
                            status = "connection_closed"
                            logging.error("Connection closed prematurely.")
                    else:
                        status = "end_pipeline"
                        for res in result:
                            if not self.config["send_raw"]:
                                res = json.dumps(res)
                            logging.info("Result: {result} \n Wasn't sent! End of pipeline!".format(
                                result=res))
                else:
                    status = "empty_result"
                    logging.info("Result is empty!")

            except Exception as e:
                status = "error"
                logging.error("Error in message handler: " + str(e))
                logging.error(cur_pipeline)
                logging.error(task)

            if self.config["send_meta"]:
                try:
                    # send report
                    await nc.publish("_reporter", json.dumps({"meta": meta,
                                                              "data": {
                                                                  "status": status,
                                                                  "new_pipeline": new_pipeline,
                                                                  "timestamp": datetime.now().strftime("%x-%X"),
                                                                  "cur_scanner": self.config["name"],
                                                                  "data": data}
                                                              }).encode())
                    logging.info("Report has been sended.")
                except Exception as e:
                    logging.error("Report sending error: " + str(e))

        if nc.is_connected:
            # Simple publisher and async subscriber via coroutine.
            await nc.subscribe(
                str(self.config["name"]) + ".>",
                self.config["name"],
                cb=message_handler
            )
            await nc.subscribe(
                str(self.config["name"]),
                self.config["name"],
                cb=message_handler
            )
            while True:
                await asyncio.sleep(3, loop=loop)

            await nc.close()

    def run(self, func):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run(loop, func))
        loop.close()
