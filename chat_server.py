import asyncio
from textwrap import dedent



# creating a class for connection pool

class ConnectionPool:

    #inintialising connection pool func
    def __init__(self):
        self.connection_pool = set()

    def send_welcome_message(self,writer):
        """
        sends a welcome message to newly connected client
        """


        # Dedent(text): This function is used to remove any common leading whitespace from every line in the input text.
        # This allows to use docstrings or embedded multi-line strings line up with the left edge 
        # of the display, while removing the formatting of the code itself.
        message = dedent(f"""
        ===============
        ( Welcome {writer.nickname}!

        There are {len(self.connection_pool) - 1} user(s)
        here beside you

        Help:
        - Type nything 
        - /list will list all the connected users
        - /quit will disconnect you

        ===============
        """)

        writer.write(f"{message}\n".encode())


    def broadcast(self,writer,message):
        
        # generates and sends to a general message to entire pool        
        for user in self.connection_pool:
            if user != writer:

                # We don't need to also broadcast to the user sending the message
                user.write(f"{message}\n".encode())



    def broadcast_user_join(self, writer):
        
        # Calls the broadcast method with a "user joining" message
        self.broadcast(writer, f"{writer.nickname} just joined")



    def broadcast_user_quit(self, writer):
        
        # Calls the broadcast method with a "user quitting" message        
        self.broadcast(writer, f"{writer.nickname} just quit")



    def broadcast_new_message(self, writer, message):
        
        # Calls the broadcast method with a user's chat message
        self.broadcast(writer, f"[{writer.nickname}] {message}")


    def list_users(self,writer):
        
        # Lists all the users in the pool
        
        message = "===\n"
        message+= "Current connected users : "
        for user in self.connection_pool:
            if user == writer:
                message += f"\n - {user.nickname} (you)"

            else:
                message += f"\n - {user.nickname}"


        message += "\n==="

        writer.write(f"{message}\n".encode())
        


    def add_new_user_to_pool(self,writer):

        # Adds a new user to our existing pool
        
        self.connection_pool.add(writer)
    

    def remove_user_from_pool(self, writer):
        
        # Removes an existing user from our pool
        
        self.connection_pool.remove(writer)



# Connecting to the remote server,writer pinging to the reader (A function from my_server.py)

async def handle_connection(reader, writer):



    # Get a nickname for the new client
    writer.write("> Choose your nickname: ".encode())
    
    # Waiting until the message is read
    response = await reader.readuntil(b"\n")

    # Displaying the response in the pool
    writer.nickname = response.decode().strip()

    # Adding a new user to the pool
    connection_pool.add_new_user_to_pool(writer)

    # Sending a Welcome message in the pool
    connection_pool.send_welcome_message(writer)

    # Anouncing the arrival of new user
    connection_pool.broadcast_user_join(writer)

    # Loop for no reading
    while True:
        try:
            data = await reader.readuntil(b"\n")
        except asyncio.exceptions.IncompleteReadError:
            connection_pool.broadcast_user_quit(writer)
            break
        
        # The help options and their conditions
        message = data.decode().strip()
        if message == "/quit":
            connection_pool.broadcast_user_quit(writer)
            break

        elif message == "/list":
            connection_pool.list_users(writer)

        else:
            connection_pool.broadcast_new_message(writer, message)

        await writer.drain()

        if writer.is_closing():
            break





    # Let's close the connection and clean up
    writer.close()

    await writer.wait_closed() # waiting nd closing function

    connection_pool.remove_user_from_pool(writer)



# Defining the main function for exectuting all the above functions 
async def main():
    server = await asyncio.start_server(handle_connection,"127.0.0.1", 8808)


    async with server:
        await server.serve_forever()


connection_pool = ConnectionPool()
asyncio.run(main())

