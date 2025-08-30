import React from 'react';
import './ProjectInfo.css';

function ProjectInfo({ onPromptClick }) {
  const capabilities = [
    {
      name: 'Analyze Vegetable Market Stall',
      prompt: 'Analyze the vegetable stall and identify all produce, including tomato, onion, cabbage, cucumber, zucchini, carrot, and beet, in this image: https://images.pexels.com/photos/2255935/pexels-photo-2255935.jpeg',
    },
    {
      name: 'Analyze Farmers Market Scene',
      prompt: 'Analyze the farmers market scene and identify all produce, like potato and onion, as well as person, plastic bag, and bucket, in this image: https://images.pexels.com/photos/12955784/pexels-photo-12955784.jpeg',
    },
    {
      name: 'Analyze Busy Street Scene',
      prompt: 'Analyze the busy street scene and identify all vehicles, such as car, bus, and truck, as well as people, in this image: https://www.livemint.com/rf/Image-621x414/LiveMint/Period1/2012/10/01/Photos/Road621.jpg',
    },
    {
      name: 'Analyze Urban Street Scene',
      prompt: 'Analyze the urban street scene and identify vehicles such as car and truck, as well as traffic lights, road signs, bicycles, and trees, in this image: https://static01.nyt.com/images/2024/04/22/multimedia/22-SUB-NAT-TEMP-TAGS-01-PRINT/nat-temp-tags-01-kvwc-articleLarge.jpg?quality=75&auto=webp&disable=upscale',
    },
    {
      name: 'Analyze City Highway with Flags',
      prompt: 'Analyze the city highway scene and identify vehicles such as car and truck, as well as flags and buildings, in this image: https://cdn.prod.website-files.com/644be23bb1119d37765bc536/680635e22693eec059833770_Observatory-launched-to-improve-road-safety-in-Saudi-Arabia.jpeg',
    },
    {
      name: 'Analyze Warehouse Workers and Inventory',
      prompt: 'Analyze the warehouse scene and identify persons, cardboard boxes, and conveyor belts in this image: https://media.business-humanrights.org/media/images/16278498935_dac4d8f223_o.2e16d0ba.fill-1000x1000-c50.jpg',
    },
  ];

  return (
    <div className="project-info">
      <div className="logo">
        <span className="logo-text">CA</span>
      </div>
      <h1 className="title">CAMEL ACI AGENT</h1>
      
      <div className="powered-by">
        <p>
          Powered by{' '}
          <a
            href="https://www.camel-ai.org/"
            target="_blank"
            rel="noopener noreferrer"
          >
            CAMEL AI
          </a>{' '}
          &amp;{' '}
          <a
            href="https://aci.dev"
            target="_blank"
            rel="noopener noreferrer"
          >
            ACI.dev
          </a>
        </p>
      </div>

      <p className="description">
        An autonomous AI agent for inventory and object detection. Select a capability below to generate a sample prompt.
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