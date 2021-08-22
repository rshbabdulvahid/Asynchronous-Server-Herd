import json
import asyncio
import aiohttp
import sys
import fcntl
import time

ports = {'Riley': 15000, 'Jaquez': 15001, 'Juzang': 15002, 'Campbell': 15003, 'Bernard': 15004}
connections = {'Riley': ['Jaquez', 'Juzang'],
               'Jaquez': ['Riley', 'Bernard'],
               'Bernard': ['Jaquez', 'Campbell', 'Juzang'],
               'Campbell': ['Bernard', 'Juzang'],
               'Juzang': ['Campbell', 'Bernard', 'Riley']}
client_locations = {}
client_times = {}
last_talked = {}
curr_server = ""

async def log_helper(file_, text, INPUT_or_OUTPUT):
    file_handler = open(file_, 'a')
    logger = ""
    if INPUT_or_OUTPUT == "INPUT":
        logger = "INPUT to " + curr_server + ": " + text + '\n'
    elif INPUT_or_OUTPUT == "OUTPUT":
        logger = "OUTPUT of " + curr_server + ": " + text + '\n'
    elif INPUT_or_OUTPUT == "DROP":
        logger = "DROPPED connection to " + text + " from " + curr_server + '\n'
    elif INPUT_or_OUTPUT == "PROPAGATE":
        logger = "RECEIVED PROPAGATE at " + curr_server + '\n'
    elif INPUT_or_OUTPUT == "END":
        logger = text + " has ended propagation\n"
    else:
        logger = "CONNECTED to " + text + " from " + curr_server + '\n'
    file_handler.write(logger)
    file_handler.close()
    
async def main(m_port):
    server = await asyncio.start_server(handle_connection, host='127.0.0.1', port=m_port)
    await server.serve_forever()

async def propagate(A, B, C, D, E):
     for server in connections[curr_server]:
            port_ = ports[server]
            reader_, writer_ = None, None
            try:
                reader_, writer_ = await asyncio.open_connection('127.0.0.1', port_)
            except:
                await log_helper(curr_server + ".txt", server, "DROP")
                continue
            propagation = "PROPAGATE " + A + " " + B + " " + C + " " + D + " " + E
            await log_helper(curr_server + ".txt", server, "CONNECT")
            writer_.write(propagation.encode())
            await writer_.drain()
            writer_.close()
            await writer_.wait_closed()

async def handle_connection(reader, writer):
    data = await reader.read()
    request = data.decode()
    fields = request.split()
    output = ""
    if not fields:
        writeback = "? " + request
        writer.write(writeback.encode())
        await log_helper(curr_server + ".txt", writeback, "OUTPUT")
        await writer.drain()
        writer.close()
        return

    if len(fields) != 4 and fields[0] != "PROPAGATE":
        writeback = "? " + request
        await log_helper(curr_server + ".txt", writeback, "OUTPUT")
        writer.write(writeback.encode())
        await writer.drain()
        writer.close()
        return

    if fields[0] == "PROPAGATE":
        await log_helper(curr_server + ".txt", request, "PROPAGATE")
    else:
        await log_helper(curr_server + ".txt", request, "INPUT")
    
    if fields[0] == "PROPAGATE":
        coordinates = None
        m_time = None
        try:
            coordinates = client_locations[fields[1]]
            m_time = client_times[fields[1]][1]
        except:
            coordinates = None
            m_time = None
        if coordinates != fields[2] or m_time != fields[4]:
            client_locations[fields[1]] = fields[2]
            client_times[fields[1]] = (fields[3], fields[4])
            last_talked[fields[1]] = fields[5]
            '''
            for server in connections[curr_server]:
                port_ = ports[server]
                reader_, writer_ = None, None
                try:
                    reader_, writer_ = await asyncio.open_connection('127.0.0.1', port_)
                except:
                    await log_helper(curr_server + ".txt", server, "DROP")
                    continue
                propagation = "PROPAGATE " + fields[1] + " " + fields[2] + " " + fields[3] + " " + fields[4] + " " + fields[5]
                await log_helper(curr_server + ".txt", server, "CONNECT")
                writer_.write(propagation.encode())
                print (server)
                writer_.close()
            '''
            await propagate(fields[1], fields[2], fields[3], fields[4], fields[5])
        await log_helper(curr_server + ".txt", curr_server, "END")
        writer.close()
        return

    elif fields[0] == "IAMAT":
        checker = fields[2].replace('+', '-')
        checker = checker.split('-')
        if len(checker) != 3:
            writeback = "? " + request
            writer.write(writeback.encode())
            await log_helper(curr_server + ".txt", writeback, "OUTPUT")
            await writer.drain()
            writer.close()
            return
        try:
            x = float(checker[1])
            y = float(checker[2])
        except:
            writeback = "? " + request
            writer.write(writeback.encode())
            await log_helper(curr_server + ".txt", writeback, "OUTPUT")
            await writer.drain()
            writer.close()
            return
        #Coordinates are valid

        client_locations[fields[1]] = fields[2]
        try:
            x = float(fields[3])
        except:
            writeback = "? " + request
            await log_helper(curr_server + ".txt", writeback, "OUTPUT")
            writer.write(writeback.encode())
            await writer.drain()
            writer.close()
            return
        client_time = float(fields[3])
        difference = time.time() - client_time
        if (difference > 0):
            difference = "+" + str(difference)
        elif (difference < 0):
            difference = str(difference)
        client_times[fields[1]] = (difference, fields[3])
        last_talked[fields[1]] = curr_server
        output = "AT " + curr_server + " " + difference + " " + fields[1] + " " + fields[2] + " " + fields[3]

        #Propagation Begins Here
        await propagate(fields[1], fields[2], difference, fields[3], curr_server)
        '''
        for server in connections[curr_server]:
            port_ = ports[server]
            reader_, writer_ = None, None
            try:
                reader_, writer_ = await asyncio.open_connection('127.0.0.1', port_)
            except:
                await log_helper(curr_server + ".txt", server, "DROP")
                continue
            propagation = "PROPAGATE " + fields[1] + " " + fields[2] + " " + difference + " " + fields[3] + " " + curr_server
            await log_helper(curr_server + ".txt", server, "CONNECT")
            writer_.write(propagation.encode())
            writer_.close()
        
        await log_helper(curr_server + ".txt", output, "OUTPUT")
        writer.write(output.encode())
        await writer.drain()
        writer.close()
        return
        '''

    elif fields[0] == "WHATSAT":
        if len(fields) != 4:
            writeback = "? " + request
            await log_helper(curr_server + ".txt", writeback, "OUTPUT")
            writer.write(writeback.encode())
            await writer.drain()
            writer.close()
            return
        try:
            x = float(fields[2])
            y = int(fields[3])
        except:
            writeback = "? " + request
            await log_helper(curr_server + ".txt", writeback, "OUTPUT")
            writer.write(writeback.encode())
            await writer.drain()
            writer.close()
            return
            
        if (int(fields[2]) > 50 or int(fields[2]) < 0 or int(fields[3]) > 20):
            writeback = "? " + request
            await log_helper(curr_server + ".txt", writeback, "OUTPUT")
            writer.write(writeback.encode())
            await writer.drain()
            writer.close()
            return

        num_results = int(fields[3])
        coordinates = None
        try:
            coordinates = client_locations[fields[1]]
        except:
            coordinates = None
        if not coordinates:
            writeback = "? " + request
            await log_helper(curr_server + ".txt", writeback, "OUTPUT")
            writer.write(writeback.encode())
            await writer.drain()
            writer.close()
            return
        index = coordinates[1:].find('+')
        if index == -1:
            index = coordinates[1:].find('-')
        index = index + 1
        coordinates = coordinates[:index] + "," + coordinates[index:]
        coordinates = coordinates.replace('+', '')
        output = ""
        async with aiohttp.ClientSession() as session:
            params = [('key', 'AIzaSyBMRQjFk8R6a_TdBNpVXc5Yd5hH6RzLXTA'), ('location', coordinates),
                      ('radius', fields[3])]
            async with session.get('https://maps.googleapis.com/maps/api/place/nearbysearch/json', params=params) as resp:
                output = await resp.json()
        jformat = output['results'][:num_results]
        temp = "AT " + last_talked[fields[1]] + " " + client_times[fields[1]][0] + " " + fields[1] + " " + client_locations[fields[1]] + " " + client_times[fields[1]][1] + "\n"
        output = temp + json.dumps(jformat, indent=4, sort_keys=True) + "\n\n"
        '''
        await log_helper(curr_server + ".txt", output, "OUTPUT")
        writer.write(output.encode())
        await writer.drain()
        writer.close()
        return
        '''

    else:
        writeback = "? " + request
        await log_helper(curr_server + ".txt", writeback, "OUTPUT")
        writer.write(writeback.encode())
        await writer.drain()
        writer.close()
        return

    await log_helper(curr_server + ".txt", output, "OUTPUT")
    await asyncio.sleep(0.5)
    writer.write(output.encode())
    await writer.drain()
    writer.close()
    return
        

if __name__ == '__main__':
    if (len(sys.argv) != 2):
        print("Incorrect arguments passed to code!")
        sys.exit(0)
    
    curr_server = sys.argv[1]
    open(curr_server+".txt", 'w').close()
    asyncio.run(main(ports[sys.argv[1]]))
