$(document).ready(function() {

    var t = 0;
    function moveit() {
        t += 0.02;
        var r = 250;
        var xcenter = 250;
        var ycenter = 250;
        var newLeft = Math.floor(xcenter + (r * Math.cos(t)));
        var newTop = Math.floor(ycenter + (r * Math.sin(t)));
        $('#box1').animate({
            top: newTop,
            left: newLeft,
        }, 1, function() {
            moveit();
        });
    }

    // play animation
    $('#btn-play').click(function() {
        moveit();
    });

    // pause animation
    $('#btn-pause').click(function() {
        $('#box1').stop();
    })

    // stop/reset animation
    $('#btn-stop').click(function() {
        $('#box1').stop()
        $('#box1').removeAttr('style')
        t = 0;
        $('#box1').css({'left':'0px', 'top':'0px'});
    });


    var object_coordinates = [];
    var timer = null;
    var interval = 100; // record every 0.1 seconds

    function recordObjectPosition() {
        object_coordinates.push($('#box1').position()); //position stored as {'left':val, 'top':val}
    };

    function stopRecordingObject() {
        clearInterval(timer);  
        timer = null;
        console.log(object_coordinates);
        object_coordinates = [];
    };

    // Record eyetracking/animation coordinates
    $('#btn-record').one("click", recordHandler1);

    ////////////////////////////////////////// handler for toggling record ON ////////////////////////////////
    function recordHandler1() {
        $('#btn-record').addClass("session-on");
        console.log('record turned ON')

        // start recording object position
        if (timer !== null) return;
        timer = setInterval(function () {
            recordObjectPosition();
        }, interval); 

        // start time
        var time = new Date($.now());

        // Alert backend to begsin storing eyetracking session + start time
        var data = {'record_eye_data': true, 'time': time}
        $.ajax({
            type: 'POST',
            url: '/_get_eyetrack_data1',
            data: JSON.stringify(data, null, '\t'),
            contentType: 'application/json;charset=UTF-8',
            dataType : "json",
            success: function(response) {
                console.log(response);
            },
            error: function(response) { 
                console.log(response.status);  
            }
        }); 
        // record object coords while session ON, start/end time
        var object_data = [];
        var object = $("#box1");
        object_data += object.position();
        var start_time = new Date($.now());
        // switch to toggle off
        $(this).one("click", recordHandler2);
    }

    //////////////////////////////// handler for toggling record OFF ////////////////////////////////
    function recordHandler2() {
        $('#btn-record').removeClass("session-on");
        console.log('record turned OFF');

        // end time
        var time = new Date($.now());

        // Alert backend to stop storing eyetracking session + end, pass end time + object's coordinates
        var data = {'record_eye_data': false, 'time': time, 'object_coordinates': object_coordinates}
        $.ajax({
            type: 'POST',
            url: '/_get_eyetrack_data2',
            data: JSON.stringify(data, null, '\t'),
            contentType: 'application/json;charset=UTF-8',
            dataType : "json",
            success: function(response) {
                console.log(response);
            },
            error: function(response) { 
                console.log(response.status);  
            }
        }); 

        stopRecordingObject();

        // switch to toggle on
        $(this).one("click", recordHandler1);
    }


    ////////////////////////////////////////////// Tracking behavior ////////////////////////////////////
    // Tracking: see if eye tracker is working
    $('#btn-track').click(function() {
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