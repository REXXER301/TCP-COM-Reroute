# TCPServer-Reroute
Reroutes a TCP Server onto com ports for lucidgloves-proto5, needs 2 pairs of linked com0com ports to work



## Installation
1. Create 2 linked com ports with [com0com](https://com0com.sourceforge.net/)<br>
   - e.g. 7->8 and 9->10
2. Change the name of the com ports in the config.json to match your just created com ports.<br>
   - e.g. **left_glove_com_port**="COM7", **right_glove_com_port**="COM9"
3. Change the **host_ip** to the ip adress of the device your server is running on.<br>
   - on windows you can find this out by running ipconfig
4. Change the **left_glove_ip** and **right_glove_ip** to the corresponding ip addresses of your gloves.<br>
   - e.g. the ip address of the esp32 in your wifi network
5. In the lucidgloves software you can now add your gloves as the **__other__** com ports.<br>
   - e.g. in the lucidgloves software the left glove com port would be COM8 and the right glove com port would be COM10
> [!IMPORTANT]
> Gloves and host pc must be connected to the same network for this to work!<br>

<br>Do not edit tcp_port and baud_rate if you don't know what you are doing.
