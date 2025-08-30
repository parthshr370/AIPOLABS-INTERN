import React from 'react';
import './ProjectInfo.css';

function ProjectInfo({ onPromptClick }) {
  const capabilities = [
    {
      name: 'Store Personal Information',
      prompt: 'I am a software developer who loves working with Python and AI. I recently moved to San Francisco and enjoy hiking on weekends.',
    },
    {
      name: 'Store Travel Memory',
      prompt: 'I went to Paris last month and visited the Eiffel Tower, Louvre Museum, and had amazing croissants at a local café near Notre-Dame.',
    },
    {
      name: 'Store Work Experience',
      prompt: 'I worked at TechCorp as a senior developer from 2020-2023, where I built machine learning pipelines and led a team of 5 engineers.',
    },
    {
      name: 'Store Learning Goals',
      prompt: 'I want to learn more about computer vision, specifically object detection models and how to deploy them in production environments.',
    },
    {
      name: 'Search Travel Memories',
      prompt: 'What do you remember about my travel experiences?',
    },
    {
      name: 'Search Work History',
      prompt: 'Tell me about my professional background and work experience.',
    },
  ];

  return (
    <div className="project-info">
      <div className="logo">
        <span className="logo-text">ACI</span>
      </div>
      <h1 className="title">ACI.DEV MEM0 DEMO</h1>
      
      <div className="powered-by">
        <p>
          Powered by{' '}
          <a
            href="https://aci.dev"
            target="_blank"
            rel="noopener noreferrer"
          >
            ACI.dev
          </a>{' '}
          &amp;{' '}
          <a
            href="https://mem0.ai"
            target="_blank"
            rel="noopener noreferrer"
          >
            MEM0
          </a>
        </p>
      </div>

      <p className="description">
        A powerful memory management demo using ACI.dev and MEM0 integration. Select a capability below to generate a sample prompt.
      </p>

      <div className="features">
        <h2 className="features-title">Core Capabilities</h2>
        <ul>
          {capabilities.map((cap) => (
            <li key={cap.name} onClick={() => onPromptClick(cap.prompt)}>
              {cap.name}
            </li>
          ))}
        </ul>
      </div>

      <div className="footer">
        CoreAxis Technologies
        <span className="year">2024</span>
      </div>
    </div>
  );
}

export default ProjectInfo;