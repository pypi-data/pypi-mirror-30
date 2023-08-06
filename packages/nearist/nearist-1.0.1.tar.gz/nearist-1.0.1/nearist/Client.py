import json

from Common import *
import socket


class Client:
    """
    This class provides the Python interface for communicating with the Nearist appliances.

    Commands are communicated via TCP/IP to the appliance server.
    """

    def __init__(self):
        self.sock = None

    @staticmethod
    def __recvall(sock, length):
        # Helper function to recv 'length' bytes or return None if EOF is hit.
        data = bytearray()

        # Loop until we've received 'length' bytes.        
        while len(data) < length:

            # Receive the remaining bytes. The amount of data returned might
            # be less than 'length'.
            packet = sock.recv(length - len(data))

            # If we received 0 bytes, the connection has been closed...            
            if not packet:
                return None

            # Append the received bytes to 'data'.    
            data += packet

        # Return the 'length' bytes of received data.
        return data

    def __on_request_complete(self, request):
        """
        Receives the response from the appliance.
        """

        # Receive 36 bytes (the side of the response message header).
        buf = Client.__recvall(self.sock, 36)

        if buf is not None:

            # Unpack the response header into a Response object.
            r = Response()
            r.unpack_header(buf)

            if r.status != Status.SUCCESS:
                raise IOError("Nearist error: %s " % Status(r.status))
            else:
                results = []

                # If there is data to receive for this response...
                if r.body_length > 0:
                    # Receive the body of this response.
                    r.body = Client.__recvall(self.sock, r.body_length)
                    r.body_checksum = Client.__recvall(self.sock, 4)
                    if r.body is not None:
                        length = r.body_length >> 3
                        if length > 0:
                            body = struct.unpack_from(("=" + ("Q" * length)), r.body, 0)

                            if request.attribute_1 == 0:
                                for i in range(0, length, 2):
                                    if body[i] != 0xFFFFFFFFFFFFFFFF and body[i + 1] != 0xFFFFFFFFFFFFFFFF:
                                        results.append({'ds_id': body[i], 'distance': body[i + 1]})
                                    else:
                                        break
                            elif request.attribute_1 == 1:
                                result = []
                                for i in range(0, length, 2):
                                    if body[i] != 0xFFFFFFFFFFFFFFFF and body[i + 1] != 0xFFFFFFFFFFFFFFFF:
                                        result.append({'ds_id': body[i], 'distance': body[i + 1]})
                                    else:
                                        results.append(result)
                                        result = []
                    else:
                        raise IOError("Read error.")
                else:
                    results = r.attribute_0
        else:
            raise IOError("Read error.")

        return results

    def __request(self, request):
        # 'sendall' will send all bytes in the request before returning.        
        status = self.sock.sendall(request.pack())

        # If the request was sent successfully... 
        # ('sendall' returns None if successful.)
        if status is None:
            return self.__on_request_complete(request)

    def open(self, host, port, api_key):
        """
        Open a socket for communication with the Nearist appliance.
        
        Parameters:
          host - IP address of the Nearist appliance.
          port - Port number for accessing the Nearist appliance.
          api_key - Unique user access key which is required to access the
                    appliance.
        
        Returns:
          None
        """

        # Convert the host name and port to a 5-tuple of arguments.
        # We just need the "address family" parameter.
        address_info = socket.getaddrinfo(host, port)

        # Create a new socket (the host and port are specified in 'connect').
        self.sock = socket.socket(address_info[0][0], socket.SOCK_STREAM)

        # Connect to the host.
        self.sock.connect((host, port))

        # Store the API key        
        self.api_key = api_key

    def close(self):
        """
        Close the socket to the Nearist appliance.
        """
        self.sock.close()

    def reset(self):
        """
        Reset the Nearist hardware, clearing all stored data.
        """

        # Create and submit a reset request.
        request = Request(self.api_key, Command.RESET)
        self.__request(request)

    def reset_timer(self):
        """
        Reset board time measurement timer.
        """

        request = Request(self.api_key, Command.RESET_TIMER)
        self.__request(request)

    def get_timer_value(self):
        """
        Get board time measurement in nanoseconds.
        """

        request = Request(self.api_key, Command.GET_TIMER)
        return self.__request(request)

    def set_distance_mode(self, mode):
        """
        Set the distance metric.
        :param mode: Common.DistanceMode
        :return:
        """

        # Create and submit the distance mode request.
        request = Request(
            self.api_key,
            Command.DISTANCE_MODE,
            mode
        )
        self.__request(request)

    def set_query_mode(self, mode):
        """
        Set query mode
        :param mode: Common.QueryMode
        :return:
        """

        request = Request(
            self.api_key,
            Command.QUERY_MODE,
            mode
        )
        self.__request(request)

    def set_read_count(self, count):
        """
        Set query result count for KNN_D/KNN_A query mode(s)
        :param count: Integer
        :return:
        """

        request = Request(
            self.api_key,
            Command.READ_COUNT,
            count
        )
        self.__request(request)

    def set_threshold(self, threshold_lower, threshold_upper=None):
        """
        Set query threshold for GT/LT/RANGE query mode(s)
        :param threshold_lower: Integer
        :param threshold_upper: Integer
        :return:
        """

        if threshold_upper is not None:
            request = Request(
                self.api_key,
                Command.THRESHOLD,
                threshold_lower,
                threshold_upper
            )
        else:
            request = Request(
                self.api_key,
                Command.THRESHOLD,
                threshold_lower
            )
        self.__request(request)

    def ds_load(self, vectors):
        """
        Load dataset to Nearist appliance
        :param vectors: List of vectors (component lists)
        :return:
        """

        if isinstance(vectors, list):
            if isinstance(vectors[0], list):
                request = Request(
                    self.api_key,
                    Command.DS_LOAD,
                    attribute_0=len(vectors[0]),
                    attribute_1=0,
                    body_length=len(vectors) * (len(vectors[0])),
                    body=vectors
                )
                self.__request(request)
            else:
                raise ValueError('Invalid argument')
        else:
            raise ValueError('Invalid argument')

    def load_dataset_file(self, file_name, dataset_name):
        """
        Load local dataset to Nearist appliance
        :param file_name: Local dataset file name
        :param dataset_name: Local dataset name
        :return:
        """

        root = json.dumps({"fileName": file_name, "datasetName": dataset_name})
        request = Request(
            self.api_key,
            Command.DS_LOAD,
            attribute_0=0,
            attribute_1=1,
            body_length=len(root),
            body=root
        )
        self.__request(request)

    def query(self, vectors):
        """
        Query for single/multiple vector(s)
        :param vectors: List of components for single query / List of vectors (component lists) for multiple query
        :return:
        """

        if isinstance(vectors, list):
            if isinstance(vectors[0], list):
                request = Request(
                    self.api_key,
                    Command.QUERY,
                    attribute_0=len(vectors[0]),
                    attribute_1=1,
                    body_length=len(vectors) * (len(vectors[0])),
                    body=vectors
                )
            else:
                request = Request(
                    self.api_key,
                    Command.QUERY,
                    attribute_0=len(vectors),
                    body_length=len(vectors),
                    body=vectors
                )
            return self.__request(request)
        else:
            raise ValueError('Invalid argument')
