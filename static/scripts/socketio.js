const socket = io();

let room = 'General';
joinRoom(room);

function leaveRoom(currentRoom) {
    socket.emit('leave', {'username': username, 'room': currentRoom});
}

function joinRoom(selectedRoom) {
    socket.emit('join', {'username': username, 'room': selectedRoom});
    displayMsgSection.innerHTML = '';
    userInputBox.focus();
}

function printSysMsg(msg) {
    const p = document.createElement('p');
    p.classList.add("chat-msg");
    p.classList.add("sys-msg");
    p.innerHTML = msg;
    displayMsgSection.append(p);
    displayMsgSection.scrollTop = displayMsgSection.scrollHeight;
}

socket.on('connect', () => {
    socket.send("I am connected!");
});

socket.on('message', data => {
    if (!data.username) {
        printSysMsg(data.msg);
        return;
    }

    const p = document.createElement('p');
    p.classList.add("chat-msg");
    p.classList.add((data.username === username) ? "current-user-msg" : "other-user-msg");

    const span_username = document.createElement('span');
    const span_timestamp = document.createElement('span');
    const span_msg = document.createElement('span');
    span_username.innerHTML = data.username;
    span_timestamp.innerHTML = data.time_stamp;
    span_msg.innerHTML = data.msg;
    p.innerHTML = span_username.outerHTML + span_msg.outerHTML + span_timestamp.outerHTML;
    displayMsgSection.append(p)

    displayMsgSection.scrollTop = displayMsgSection.scrollHeight;

});

sendMessageBtn.addEventListener('click', () => {
    socket.send({'msg': userInputBox.value, 'username': username, 'room': room});
    userInputBox.value = '';
});

roomSelection.forEach(p => {
    p.addEventListener('click', () => {
        let newRoom = p.innerHTML;
        if (newRoom == room) {
            let msg = `You are already in ${room}`;
            printSysMsg(msg);
        } else {
            leaveRoom(room);
            joinRoom(newRoom);
            room = newRoom;
        }
        sidebar.classList.toggle("active");
        rightsidePanel.classList.toggle("active");
    });
});
