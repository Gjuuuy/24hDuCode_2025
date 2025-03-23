"use client";

import { useState, useEffect, useRef } from "react";
import axios from "axios";

export default function ChatPage() {
  const [messages, setMessages] = useState<{ role: string; text: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [speechAvailable, setSpeechAvailable] = useState(true);

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);

  useEffect(() => {
    if (typeof window !== "undefined" && ("webkitSpeechRecognition" in window || "SpeechRecognition" in window)) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = "fr-FR";
      recognition.continuous = false;
      recognition.interimResults = false;

      recognition.onstart = () => setIsListening(true);
      recognition.onend = () => setIsListening(false);
      recognition.onerror = (event) => console.error("Erreur reconnaissance vocale :", event);

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript); // Ajoute le texte reconnu dans l'input
      };

      recognitionRef.current = recognition;
    } else {
      setSpeechAvailable(false); // Désactive le bouton si la reconnaissance vocale n'est pas dispo
    }
  }, []);

  const startListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.start();
    }
  };

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", text: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await axios.post("http://127.0.0.1:52001/chat", {
        message: input,
      });

      const botMessage = { role: "bot", text: response.data.response };
      setMessages((prev) => [...prev, botMessage]);

      readMessage(response.data.response);
    } catch (error) {
      console.error("Erreur API :", error);
      alert("Erreur lors de l'envoi du message, veuillez réessayer !");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      sendMessage();
    }
  };

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

 // Fonction pour redémarrer la conversation
 const restartConversation = async () => {
  // Réinitialiser les messages dans l'état
  setMessages([]);

  try {
    // Effectuer la requête pour redémarrer l'état du backend
    await axios.post("http://127.0.0.1:52001/restart");
    console.log("Conversation redémarrée !");
    // Après avoir redémarré, faire un appel pour accueillir l'utilisateur
    await getGreetingMessage();
  } catch (error) {
    console.error("Erreur lors du redémarrage de la conversation :", error);
    alert("Erreur lors du redémarrage de la conversation, veuillez réessayer !");
  }
};

    // Fonction pour obtenir le message d'accueil du bot
    const getGreetingMessage = async () => {
      try {
        const response = await axios.post("http://127.0.0.1:52001/chat", {
          message: "Présentes-toi brievement",
        });
        const botMessage = { role: "bot", text: response.data.response };
        setMessages((prev) => [...prev, botMessage]);
  
        // Lire le message d'accueil du bot
        readMessage(response.data.response);
      } catch (error) {
        console.error("Erreur lors de l'appel API pour le message d'accueil :", error);
        alert("Erreur lors du chargement du message d'accueil.");
      }
    };

  const readMessage = (message: string) => {
    if (isSpeaking) {
      speechSynthesis.cancel();
    }

    const speech = new SpeechSynthesisUtterance(message);
    speech.lang = "fr-FR";
    speech.volume = 1;
    speech.rate = 1;
    speech.pitch = 1;

    speech.onstart = () => setIsSpeaking(true);
    speech.onend = () => setIsSpeaking(false);

    speechSynthesis.speak(speech);
  };

  // Faire un appel API dès le chargement de la page pour le message d'accueil
  useEffect(() => {
    getGreetingMessage();
  }, []);

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-900 text-white p-4">
      <div className="max-w-2xl w-full bg-gray-800 p-6 rounded-2xl shadow-md">
        <h1 className="text-2xl font-bold mb-4">💬 Chat avec l'IA</h1>
        <div className="h-80 bg-gray-700 p-4 rounded-lg overflow-y-auto">
          {messages.map((msg, i) => (
            <p key={i} className={msg.role === "user" ? "text-blue-400" : "text-green-400"}>
              {msg.role === "user" ? "👤" : "🤖"} {msg.text}
            </p>
          ))}
          {loading && <p className="text-green-400">🤖 Le bot est en train de réfléchir...</p>}
          <div ref={messagesEndRef} />
        </div>
        <div className="mt-4 flex">
          <input
            type="text"
            placeholder="Écris un message..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyPress}
            className="flex-1 p-2 rounded-lg bg-gray-600 text-white outline-none"
          />
          <button
            onClick={sendMessage}
            className="ml-2 px-4 py-2 bg-blue-500 rounded-lg hover:bg-blue-600"
          >
            Envoyer
          </button>
          <button
            onClick={startListening}
            disabled={!speechAvailable} // Désactive le bouton si la reconnaissance vocale n'est pas dispo
            className={`ml-2 px-4 py-2 rounded-lg ${isListening ? "bg-red-500" : speechAvailable ? "bg-gray-500" : "bg-gray-700"} hover:bg-red-600`}
          >
            🎙️
          </button>
        </div>
        {!speechAvailable && (
          <p className="text-red-400 mt-2 text-sm">⚠️ La reconnaissance vocale n'est pas disponible sur votre navigateur.</p>
        )}
        <div className="mt-4 flex justify-between">
          <button
            onClick={restartConversation}
            className="px-4 py-2 bg-red-500 rounded-lg hover:bg-red-600"
          >
            Redémarrer
          </button>
        </div>
      </div>
    </div>
  );
}
