
import struct
from pymodbus.mei_message import ReadDeviceInformationResponse


# The __ does not allow simple subclassing
class ReadEBSDeviceInformationResponse(ReadDeviceInformationResponse):
    def decode(self, data):
        params = struct.unpack('>BBBBBB', data[0:6])
        self.sub_function_code, self.read_code = params[0:2]
        self.conformity, self.more_follows = params[2:4]
        self.next_object_id, self.number_of_objects = params[4:6]
        self.information, count = {}, 6  # skip the header information

        while count < len(data):
            object_id, object_length = struct.unpack('>BB', data[count:count+2])
            count += object_length + 2
            if object_id not in self.information.keys():
                self.information[object_id] = data[count-object_length:count]
            else:
                if isinstance(self.information[object_id], list):
                    self.information[object_id].append(data[count-object_length:count])
                else:
                    self.information[object_id] = [self.information[object_id],
                                                   data[count - object_length:count]]

    def __str__(self):
        return "ReadEBSDeviceInformationResponse(%d)" % self.read_code
