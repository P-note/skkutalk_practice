function getTime() {
    time = new Date();
    hour = time.getHours();
    min = time.getMinutes();
    timeinfo = ""
    if (hour >= 12)
        timeinfo += "오후"
    else
        timeinfo += "오전"
    timeinfo = timeinfo + ' ' + hour % 12 + ':' + (min < 10 ? '0' : '') + min;

    return timeinfo;
}

function addmsg_ui(msgs) {
    var message_obj = msgs;
    var message_list = $('#ul_msg');
    var time = message_obj['time'];
    var msg = message_obj['content'];
    var sender = message_obj['sender']
    msg = msg.replace(/\n/gi, "<br>");
    uid = $("#username").text();
    if (uid != sender) {
        message_list.append("<div class='nick'>" + sender + "</div><li class='opchatbox'><div class='opchat'>" + msg + "</div>" + "<span>" + time + "</span></li>");
        // console.log(msg);
    }
    else {
        message_list.append("<li class='mychatbox'><span>" + time + "</span>" + "<div class='mychat'>" + msg + "</div></li>");
        // console.log(msg);
    }
    $('.frame').scrollTop($('.frame')[0].scrollHeight);
}

$(document).ready(function () {
    
    function update_msgs(msgs) {
        $("#ul_msg").empty();
        var message_list = $('#ul_msg');
        var username = $("#username").text();
        msgs.forEach(item => {
            var sender = item['sender'];
            var time = item['time'];
            var msg = item['content'];
            if (sender != username) {
                message_list.append("<div class='nick'>" + sender + "</div><li class='opchatbox'><div class='opchat'>" + msg + "</div>" + "<span>" + time + "</span></li>");
                // console.log(msg);
            }
            else {
                message_list.append("<li class='mychatbox'><span>" + time + "</span>" + "<div class='mychat'>" + msg + "</div></li>");
                // console.log(msg);
            }
            $('.frame').scrollTop($('.frame')[0].scrollHeight);
            // console.log(item);
        });
    }
    
    var chatroom_id = sessionStorage.getItem('cid');
    var username = $("#username").text();
    var op = sessionStorage.getItem('op');
    $("#op_title").append(op);
    console.log(chatroom_id, op);

    var cidata = {"id":chatroom_id};
    $.ajax({
        url: "/get_chatlog",
        type: "post",
        contentType: "application/json",
        data: JSON.stringify(cidata),
        success: update_msgs
    });

    var ws = new WebSocket("ws://localhost:8000/ws");
    
    ws.onmessage = function (event) { //assemble message
        var data = JSON.parse(event.data);
        var chatroom_id = sessionStorage.getItem('cid');
        var uid = $("#username").text();
        var sender = data.sender;
        //need to check that this message isn't from self.
        if ((chatroom_id == data.chatroom_id) && (uid != sender)) {
            addmsg_ui(data);
        }
    };
    function sendMessage(event) { //sendmessage when clicking button
        var content = $("#msg_input").val();
        var uid = $("#username").text();
        var chatroom_id = sessionStorage.getItem('cid');
        var op = sessionStorage.getItem('op');
        content = content.replace(/\n/gi, "<br>");
        if (content != '') {
            var data = JSON.stringify({"chatroom_id":chatroom_id, "sender": uid, "receiver": op, "content": content, "time": getTime() });
            console.log(data);
            ws.send(data)
            $("#msg_input").val('');
            //add message log to db.
            $.ajax({
                url: "/addmsg",
                type: "post",
                contentType: "application/json",
                data: data,
                success: addmsg_ui
            });

            var data2 = JSON.stringify({"id":chatroom_id, "sender": uid, "receiver": op, "latest": content});
            $.ajax({
                url: "/update_latest",
                type: "post",
                contentType: "application/json",
                data: data2,
            });
            console.log(uid + "addmsg worked")
        }

    }

    $('textarea').on('keyup', function (e) {
        if (e.keyCode == 13)
            if (!e.shiftKey) {
                e.preventDefault();
                // tid = e.target.id
                msg = $("#msg_input").val();
                if (msg != '\n')
                    sendMessage();
                else
                    $("#msg_input").val('');
            }
    });

    $("#btn_send").click(function (event) {
        sendMessage(event);
    });

});


