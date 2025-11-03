async function sendMessage() {
  const message = document.getElementById("message").value;
  const chatDiv = document.getElementById("chat");
  
  chatDiv.innerHTML += `<p><b>You:</b> ${message}</p>`;
  document.getElementById("message").value = "";

  const response = await fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  });

  const data = await response.json();
  chatDiv.innerHTML += `<p><b>Verona:</b> ${data.reply}</p>`;
  chatDiv.scrollTop = chatDiv.scrollHeight;
}
