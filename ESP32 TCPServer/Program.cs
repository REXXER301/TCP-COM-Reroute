using System;
using System.Collections.Generic;
using System.Linq;
using System.Net.Sockets;
using System.Net;
using System.Text;
using System.IO;
using System.IO.Ports;
using System.Threading;

namespace ESP32_TCPServer
{
    class Program
    {
        const string host = ""; // IP address of Server
        const string left_glove = "";         //IP adress of left glove
        const string right_glove = "";        ////IP adress of right glove

        const int port = 65432; //Port to listen on (non-privileged ports are > 1023)
        SerialPort serialPort;  //COM Port left:7->8 & right:9->10
        static void Main(string[] args)
        {
            Program main = new Program();
            main.server_start();  //starting the server for left glove

            Console.ReadLine();
        }

        TcpListener server = new TcpListener(IPAddress.Parse(host), port);
        TcpClient client;
        NetworkStream stream;
        StreamReader reader;
        StreamWriter writer;
        private void server_start()
        {
            server.Start();
            accept_connection();  //accepts incoming connections
        }

        private void accept_connection()
        {
            server.BeginAcceptTcpClient(handle_connection, server);  
        }

        private void handle_connection(IAsyncResult result)  //used to communicate between threads
        {
            accept_connection(); 
            client = server.EndAcceptTcpClient(result);  
            string connected_ip = client.Client.RemoteEndPoint.ToString();
            Console.WriteLine(connected_ip + " has connected");

            if (connected_ip.Split(':')[0] == left_glove) 
            {
                serialPort = new SerialPort("COM7"); // 7->8
            }
            else if (connected_ip.Split(':')[0] == right_glove) // right glove
            {
                serialPort = new SerialPort("COM9"); // 9->10
            }
            else {
                Console.WriteLine("unknown device connected");
                return;
            }

            stream = client.GetStream();
            reader = new StreamReader(stream);
            writer = new StreamWriter(stream) { AutoFlush = true };

            while (serialPort.IsOpen)
                Thread.Sleep(500);
            while (true)
            {
                Thread.Sleep(500);
                try
                {
                    serialPort.Open();
                    serialPort.BaudRate = 115200;
                    break;
                }
                catch (Exception) {

                }
            }
            Console.WriteLine("Port " + serialPort.PortName + " connected");
            closing += closePort;
            message_thread = new Thread(messager);
            respond_thread = new Thread(responder);
            message_thread.Start();
            respond_thread.Start();

        }
        Thread message_thread, respond_thread;
        private void messager()
        {
            while (client.Connected)
            {
                string message = reader.ReadLine();
                Console.WriteLine(message);
                serialPort.WriteLine(message);
            }
            closing.Invoke();
        }
        private void responder() {
            while (client.Connected)
            {
                string response = serialPort.ReadLine();
                writer.WriteLine(response);
            }
            closing.Invoke();
        }

        private delegate void voidDelegate();
        private voidDelegate closing;
        private void closePort() {
            respond_thread.Abort();
            message_thread.Abort();
            serialPort.Close();
            Console.WriteLine("Connection closed");
        }

    }
}
