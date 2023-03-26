from mmcore.services import client
import rhino3dm

dd=client.get_connection_by_host_port(*(("localhost",4777),))
models=dd.root.getmodule("models")

with open("/Users/andrewastakhov/Downloads/Telegram Desktop/Ванты в истинных координатах.txt") as f:
    cx=models.CxmFormat(f.read())

rhino3dm.File3dm.Decode(encoded).Write(os.getcwd()+"/test.3dm",7)
