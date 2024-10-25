import socket
import os
import mimetypes as mime #to determine the mimetype of the response

#Defining the host address and the port which server is running
#http://localhost:2728/

#localhost IP and the port we need to run the server
SERVER_HOST = '127.0.0.1'
PORT = 2728

# Create socket
#AF_INET is for IPV4 family and for socket type .SOCK_STREM=> to denote the type as TCP
webserver_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
webserver_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

#Binding the host and the port and make it listen for incoming requests
webserver_socket.bind((SERVER_HOST, PORT))
webserver_socket.listen(1)

print(f'Server is running and listning on port {PORT}')


#Function for getting the cleaned resource path
def getResource(path):
    if path.endswith('/'):  # Ex: /home/
        path = path[0:-1]  #Remove the ending /

    path_segments = path.split('.') #Splitting by . to check for extensions

    if not (path == ''):
        if len(path_segments) > 1:
            #Requesting file with extension
            html_path = os.path.join(os.getcwd(), "htdocs", path[1:])
        else:
            #Requesting file without extension
            html_path = os.path.join(os.getcwd(), "htdocs", f"{path[1:]}.html")
    
    else: 
        #Requesting root
        html_path = os.path.join(os.getcwd(), "htdocs", "index.html")
    
    #Printing each request and returning the cleaned path
    print(f"Requesting -> {html_path}")
    return html_path   

while True:    
    #Wait for HTTP client connections
    client_connection, client_address = webserver_socket.accept()

    #Get the client request and print it to terminal
    client_request = client_connection.recv(1024).decode()

    #Parse HTTP header and get the raw header
    http_headers = client_request.split('\r\n')
    
    #Extracting the start line of the HTTP request
    startline = http_headers[0]
    try:
        #getting the file path
        req_filename_path = startline.split(' ')[1]
        #Splitting the url by query parameter notation
        http_path = req_filename_path.split('?')[0]
        
        filename = getResource(http_path)

        try:
            #Picking up the file, open and reading it
            filepath = os.path.join(os.getcwd(), "htdocs",filename)
            res_file = open(filepath, "r")
            content = res_file.read()
            res_file.close()

            #Setting the mimetype
            content_type = mime.guess_type(filepath)

            #Final response
            response = f"HTTP/1.1 200 OK\r\nServer: Python:HTTP[Custom]\r\nContent-Length: {len(content)}\r\nContent-Type: {content_type[0]}\r\n\n{content}"

        except FileNotFoundError: #If file not found in the server
            filepath = os.path.join(os.getcwd(), "htdocs","error.html")
            res_file = open(filepath, "r")
            content = res_file.read()
            res_file.close()

            #Final response with 404 Error page
            response = 'HTTP/1.1 404 NOT FOUND\n\n' + content
    
    except IndexError: #Error in making the request
        response = "HTTP/1.1 400 Bad Request"

    #Sending the whole buffer
    client_connection.sendall(response.encode())
    
    #End the connection
    client_connection.close()
    
# Close socket
webserver_socket.close()

