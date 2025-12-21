const input = document.getElementById("input");
const chat = document.getElementById("chat");

input.addEventListener("keydown", async (e) => {
  if (e.key !== "Enter") return;

  const text = input.value;
  input.value = "";

  addMessage(text, "user");

  const res = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({
      messages: [{ role: "user", content: text }]
    })
  });

  const reader = res.body.getReader();
  let assistantMsg = addMessage("", "assistant");

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    assistantMsg.textContent += new TextDecoder().decode(value);
  }
});

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  chat.appendChild(div);
  return div;
}
