Example
=======

.. code:: python

    #!/usr/bin/env python3

    import hclib


    # Make a callback function with two parameters.
    def on_message(connector, data):
        # The second parameter (<data>) is the data received.
        print(data)
        print(connector.onlineUsers)
        # Checks if someone joined the channel.
        if data["type"] == "online add":
            # Sends a greeting the person joining the channel.
            connector.send("Hello {}".format(data["nick"]))


        if __name__ == "__main__":
            hclib.HackChat(on_message, "myBot", "botDev")

Documentation
=============

1. Open the interactive Python console:
    - Windows: ``python``
    - Other: ``python3``
2. Import the module: ``import hclib``
3. Generate the documentation: ``help(hclib)``
