import socket
import sys
import traceback
import os
import mimetypes

class HttpServer():

    def __init__(self, port):
        self.port = port

    def get_path(self, request):
        """
        takes the request, and returns just
        the path
        """
        content = request.split(" ")
        path = " "

        for value in content:
            if "/" in value:
                path = value
                break
        return path.strip()

    def get_content(self, path):
        """
        takes the path and returns content of the
        file if the path representa a file, or 
        it returns a list of files inside the directory
        if the path represents a directory
        """
        content = ""

        file_path = path.split("/")
        filename = ''.join(file_path[-1:])
        # print(f"\nFile name: {filename}")

        if os.path.isfile(filename):
            print(f"\nIt is a file.")
            with open(filename, 'rb') as f:
                reader = f.read(1024)
                content += reader
        elif os.path.isdir(filename):
            print(f"\nIt is a director.")
            content = os.listdir(filename)

        return content

    def get_mimetype(self, path):
        """
        This tells the browser what type the content is.
        It would tell the browser that this is image if the 
        content is an image, the browser then renders the 
        contents of the response as an image, 
        or this is a web page if the
        content is a html type, the browser then renders the
        content as a web page.
        The mime-type needs to figure out what type the 
        content is based on the path we give it
        """
        mime = mimetypes.MimeTypes()
        mime_type, _ = mime.guess_type(path)
        return mime_type


    def make_response(self, res_code, res_description, res_body, res_mime):
        """
        It takes, the response-code, response-description, response-body
        and response-mimetype and builds appropriate reponse out of the 
        parameters
        """
        response = "HTTP/1.1 {} {}\r\n".format(res_code, res_description)
        response += "Content-Type: {}".format(res_mime)
        response += "\r\n"
        response += "{}".format(res_body)
        
        return response
    
    def serve(self):
        """
        This method has the basic structure of TCP server.
        When this method is called, it starts an infinit
        loop of accepting and then closing connections.
        It accepts connection, does something with the 
        response accepted from the connection, and then
        closes the connetion.
        """
        address = ('0.0.0.0', port)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        print("making a server on {0}:{1}".format(*address))
        print("Visit http://localhost:{}".format(port))

        sock.bind(address)
        sock.listen(10)

        try:
            while True:
                print('waiting for a connection')
                conn, addr = sock.accept()  # blocks until a connection arrives
                try:
                    print('connection - {0}:{1}'.format(*addr))

                    # byte_size = 1024
                    request = ''
                    
                    while True:
                        data = conn.recv(1024)
                        request += data.decode()

                        if '\r\n\r\n' in request:
                            break

                    path = self.get_path(request)

                    try:
                        body = self.get_content(path)
                        mimetype = self.get_mimetype(path)

                        response = self.make_response(
                            b"200",
                            b"OK",
                            body,
                            mimetype
                        )
                    except FileNotFoundError:
                        body = b"Count't find the file you requested"
                        mimetype = b"text/plain"

                        response = self.make_response(
                            b"404",
                            b"NOT FOUND",
                            body,
                            mimetype
                        )

                    conn.sendall(response.encode("utf8"))

                except:
                    traceback.print_exc()
                finally:
                    conn.close() 

        except KeyboardInterrupt:
            sock.close()
            return
        except:
            traceback.print_exc()


if __name__ == '__main__':
    try:
        port = int(sys.argv[1])
    except IndexError:
        port = 10000 

    server = HttpServer(port)
    server.serve()

