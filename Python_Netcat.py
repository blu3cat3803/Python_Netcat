import sys
import socket
import getopt
import threading
import subprocess

listen = False
command = False
upload = False
execute = ""
target = ""
upload_destination = ""
port = 0

def usage():
	print("Python Netcat Tool")
	print()
	print("EX: Python_Netcat.py -t target_host -p port")
	print("-l --listen")
	print("-e --execute=file_to_run")
	print("-c --command")
	print("-u -upload=destination")
	print()
	print()
	sys.exit(0)

def client_sender(send_buffer):
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	try:
		client.connect((target, port))

		if len(send_buffer):
			msg = send_buffer.encode()
			client.send(msg)

		while True:
			recv_len = 1
			response = ""

			while recv_len:
				data = client.recv(4096).decode("utf-8")
				recv_len = len(data)
				response += data
				if recv_len < 4096:
					break

			print(response)
			send_buffer = input("")
			send_buffer += "\n"

			client.send(send_buffer.encode())
	except:
		print("Existing...")
		client.close()

def client_handler(client_socket):
	global upload
	global execute
	global command

	if len(upload_destination):
		file_buffer = ""

		while True:
			data = client_socket.recv(4096).decode("utf-8")
			if not data:
				break
			else:
				file_buffer += data

		try:
			file_descriptor = open(upload_destination, "wb")
			file_descriptor.write(file_buffer)
			file_descriptor.close()

			client_socket.send("Successfully saved.".encode())
		except:
			client_socket.send("Failed".encode())

	if len(execute):
		output = run_command(execute)

		client_socket.send(output.encode())
	
	if command:
		while True:
			client_socket.send("PNT:# ".encode())
			cmd_buffer = ""
			while "\n" not in cmd_buffer:
				cmd_buffer += client_socket.recv(1024).decode("gbk")
				response = run_command(cmd_buffer)

				client_socket.send(response.encode())

def server_loop():
	global target

	if not len(target):
		target = "0.0.0.0"

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.bind((target, port))
	server.listen(5)

	while True:
		client_socket, addr = server.accept()

		print("[*]Accepted connection from: %s:%d" % (target, port))
		client_thread = threading.Thread(target=client_handler, args=(client_socket, ))
		client_thread.start()

def run_command(command):
	command = command.rstrip()

	try:
		output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True, universal_newlines=True)
	except:
		output = "Command Error!\n"

	return output

def main():
	global listen
	global command
	global upload
	global execute
	global port
	global target

	try:
		opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu", ["help", "listen", "execute", "target", "port", "command", "upload"])
	except getopt.GetoptError as err:
		print(str(err))
		usage()
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
		elif o in ("-l", "--listen"):
			listen = True
		elif o in ("-e", "--execute"):
			execute = a
		elif o in ("-c", "--commandshell"):
			command = True
		elif o in ("-u", "--upload"):
			upload_destination = a
		elif o in ("-t", "--target"):
			target = a
		elif o in ("-p", "--port"):
			port = int(a)
		else:
			assert False, "No parameter or Wrong parameter."
	
	if not listen and len(target) and port > 0:
		send_buffer = sys.stdin.read()
		client_sender(send_buffer)

	if listen:
		print("Listening...")
		server_loop()
main()