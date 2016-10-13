$(document).ready(function() {

    var t = 0;
    function moveit() {
        t += 0.025;
        var r = 200;
        var xcenter = 200;
        var ycenter = 200;
        var newLeft = Math.floor(xcenter + (r * Math.cos(t)));
        var newTop = Math.floor(ycenter + (r * Math.sin(t)));
        $('#box1').animate({
            top: newTop,
            left: newLeft,
        }, 1, function() {
            moveit();
        });
    }

    $('#btn-play').click(function() {
        moveit();
    });

    $('#btn-pause').click(function() {
        $('#box1').stop();
    })

    $('#btn-stop').click(function() {
        $('#box1').stop()
        $('#box1').removeAttr('style')
        t = 0;
        $('#box1').css({'left':'0px', 'top':'0px'});
    });

    $('#btn-track').click(function() {
        console.log('clicked track');

        // Use a "/test" namespace.
        // An application can open a connection on multiple namespaces, and
        // Socket.IO will multiplex all those connections on a single
        // physical channel. If you don't care about multiple channels, you
        // can set the namespace to an empty string.
        namespace = '/test';

        // Connect to the Socket.IO server.
        // The connection URL has the following format:
        //     http[s]://<domain>:<port>[/<namespace>]
        var socket = io.connect('http://' + document.domain + ':' + location.port + namespace);

        // Event handler for new connections.
        // The callback function is invoked when a connection with the
        // server is established.
        socket.on('connect', function() {
            socket.emit('my_event', {data: 'I\'m connected!'});
        });

        // Event handler for server sent data.
        // The callback function is invoked whenever the server emits data
        // to the client. The data is then displayed in the "Received"
        // section of the page.
        socket.on('my_response', function(msg) {
            var data = msg.data;
            var avg_eye_coordinate = msg.data['avg'];

            if (avg_eye_coordinate) {
                var x_pos = avg_eye_coordinate['x'];
                var y_pos = avg_eye_coordinate['y'];

                var c = document.getElementById('cursor');
                c.style.left = x_pos+'px';
                c.style.top = y_pos+'px';    
            }
        });

        // Interval function that tests message latency by sending a "ping"
        // message. The server then responds with a "pong" message and the
        // round trip time is measured.
        var ping_pong_times = [];
        var start_time;
        window.setInterval(function() {
            start_time = (new Date).getTime();
            socket.emit('my_ping');
        }, 1000);

        // Handler for the "pong" message. When the pong is received, the
        // time from the ping is stored, and the average of the last 30
        // samples is average and displayed.
        socket.on('my_pong', function() {
            var latency = (new Date).getTime() - start_time;
            ping_pong_times.push(latency);
            ping_pong_times = ping_pong_times.slice(-30); // keep last 30 samples
            var sum = 0;
            for (var i = 0; i < ping_pong_times.length; i++)
                sum += ping_pong_times[i];
            $('#ping-pong').text(Math.round(10 * sum / ping_pong_times.length) / 10);
        });

        // Handlers for the different forms in the page.
        // These accept data from the user and send it to the server in a
        // variety of ways
        $('form#emit').submit(function(event) {
            socket.emit('my_event', {data: $('#emit_data').val()});
            return false;
        });
        $('form#broadcast').submit(function(event) {
            socket.emit('my_broadcast_event', {data: $('#broadcast_data').val()});
            return false;
        });
        $('form#disconnect').submit(function(event) {
            socket.emit('disconnect_request');
            return false;
        });
    });

   
});