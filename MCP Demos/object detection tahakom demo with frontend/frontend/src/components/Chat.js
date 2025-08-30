import React, { useState, useRef, useEffect } from 'react';
import Message from './Message';
import ToolList from './ToolList';
import './Chat.css';

function Chat({ promptText }) {
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      text: 'Hello! I am the CAMEL ACI Agent, an image analysis assistant specialized in object detection. I can analyze images to identify and locate objects. Share an image URL with me, and I\'ll help you detect objects in it!',
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    // When a prompt is clicked in the side panel, update the input field
    if (promptText) {
      setInputValue(promptText);
    }
  }, [promptText]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    const userMessage = { sender: 'user', text: inputValue };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: inputValue }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      let agentResponseText = "Sorry, I couldn't get a response.";
      let executedTools = [];

      if (data.error) {
        agentResponseText = data.error;
      } else if (data.response) {
        agentResponseText = data.response;
        executedTools = data.executed_tools || [];
      }

      const agentMessage = {
        sender: 'agent',
        text: agentResponseText,
        executed_tools: executedTools,
      };
      setMessages((prevMessages) => [...prevMessages, agentMessage]);
    } catch (error) {
      console.error('Error communicating with the agent:', error);
      const errorMessage = {
        sender: 'agent',
        text: 'I am having trouble connecting to my brain right now. Please try again later.',
      };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-container">
      <ToolList />
      <div className="messages-window">
        {messages.map((msg, index) => (
          <Message key={index} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      {isLoading && (
        <div className="loading-indicator-wrapper">
          <div className="loading-dots">
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
          <span>Agent is thinking...</span>
        </div>
      )}
      <div className="input-area">
        <form onSubmit={handleSendMessage} className="input-form">
          <input
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Paste an image URL and ask what objects to detect..."
            autoFocus
            disabled={isLoading}
          />
          <button type="submit" disabled={!inputValue.trim() || isLoading}>
            Send
          </button>
        </form>
      </div>
    </div>
  );
}

export default Chat; 