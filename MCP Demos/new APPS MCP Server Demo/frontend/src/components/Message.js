import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './Message.css';

function Message({ message }) {
  const { sender, text, executed_tools } = message;

  // Custom renderers for markdown elements
  const components = {
    img: ({ node, ...props }) => (
      <img {...props} className="markdown-image" alt={props.alt || "Agent response image"} />
    ),
    table: ({ node, ...props }) => (
      <div className="table-container">
        <table {...props} className="markdown-table" />
      </div>
    ),
    th: ({ node, ...props }) => (
      <th {...props} className="markdown-th" />
    ),
    td: ({ node, ...props }) => (
      <td {...props} className="markdown-td" />
    ),
    a: ({ node, ...props }) => (
      // eslint-disable-next-line jsx-a11y/anchor-has-content
      <a {...props} target="_blank" rel="noopener noreferrer" />
    )
  };

  return (
    <div className={`message-wrapper ${sender}`}>
      <div className="message-sender">
        {sender === 'user' ? 'You' : 'Agent'}
      </div>
      <div className="message-content">
        <ReactMarkdown 
          remarkPlugins={[remarkGfm]}
          components={components}
        >
          {text}
        </ReactMarkdown>
      </div>
      {executed_tools && executed_tools.length > 0 && (
        <div className="executed-tools-container">
          <h4 className="executed-tools-title">TOOLS EXECUTED</h4>
          <ul className="executed-tools-list">
            {executed_tools.map((tool, index) => (
              <li key={index}>{tool}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default Message; 