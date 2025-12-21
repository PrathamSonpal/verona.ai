import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-app.js";
import { getAuth, signInWithEmailAndPassword } from "https://www.gstatic.com/firebasejs/10.7.0/firebase-auth.js";

const firebaseConfig = {
    apiKey: "AIzaSyBAiro_eGeNuNVM_g6X-SL_F0G0xXcQqqE",
    authDomain: "verona-ai.firebaseapp.com",
    projectId: "verona-ai",
    storageBucket: "verona-ai.firebasestorage.app",
    messagingSenderId: "722435640612",
    appId: "1:722435640612:web:a78f026d555c80acae37b1"
  };


const app = initializeApp(firebaseConfig);
const auth = getAuth(app);

let token = null;
let messages = [];

window.login = async () => {
  const email = emailInput.value;
  const password = passwordInput.value;

  const userCred = await signInWithEmailAndPassword(auth, email, password);
  token = await userCred.user.getIdToken();

  document.getElementById("login").hidden = true;
  document.getElementById("app").hidden = false;
};

const input = document.getElementById("input");
const chat = document.getElementById("chat");

input.addEventListener("keydown", async (e) => {
  if (e.key !== "Enter") return;

  const text = input.value.trim();
  input.value = "";

  addMessage(text, "user");
  messages.push({ role: "user", content: text });

  const res = await fetch("https://YOUR-CLOUDFLARE-TUNNEL/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + token
    },
    body: JSON.stringify({ messages })
  });

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let assistantDiv = addMessage("", "assistant");
  let full = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    full += decoder.decode(value);
    assistantDiv.textContent = full;
  }

  messages.push({ role: "assistant", content: full });
});

function addMessage(text, role) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.textContent = text;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}
