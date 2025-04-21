const ws = new WebSocket("ws://localhost:8000/ws");
const chat = document.getElementById("chat");
const sendButton = document.getElementById("btn-send");

ws.onmessage = (event) => {
  const li = document.createElement("li");
  li.textContent = event.data;
  chat.appendChild(li);
};

sendButton.addEventListener("click", () => {
  const input = document.getElementById("msg");
  if (input.value) {
    ws.send(input.value);
    input.value = "";
  }
});
