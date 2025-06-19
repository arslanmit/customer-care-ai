import React, { useState, useEffect } from 'react';
import { 
  Chart as ChartJS, 
  CategoryScale, 
  LinearScale, 
  BarElement, 
  Title, 
  Tooltip, 
  Legend,
  ArcElement
} from 'chart.js';
import { Bar, Pie } from 'react-chartjs-2';

// Register the components needed for the charts
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

const Analytics = ({ conversationHistory }) => {
  const [messageStats, setMessageStats] = useState({
    userCount: 0,
    botCount: 0,
    avgResponseTime: 0,
    intentDistribution: {}
  });

  useEffect(() => {
    if (conversationHistory && conversationHistory.length > 0) {
      // Calculate basic message statistics
      const userMessages = conversationHistory.filter(msg => msg.sender === 'user');
      const botMessages = conversationHistory.filter(msg => msg.sender === 'bot');
      
      // Mock intent distribution (in a real app, this would come from Rasa)
      const mockIntents = {
        'greet': Math.floor(Math.random() * 5),
        'ask_info': Math.floor(Math.random() * 5),
        'tell_joke': Math.floor(Math.random() * 5),
        'ask_time': Math.floor(Math.random() * 5),
        'goodbye': Math.floor(Math.random() * 5)
      };
      
      // Update stats
      setMessageStats({
        userCount: userMessages.length,
        botCount: botMessages.length,
        avgResponseTime: Math.floor(Math.random() * 500) + 200, // Mock response time in ms
        intentDistribution: mockIntents
      });
    }
  }, [conversationHistory]);

  const messageCountData = {
    labels: ['User Messages', 'Bot Responses'],
    datasets: [
      {
        label: 'Message Count',
        data: [messageStats.userCount, messageStats.botCount],
        backgroundColor: ['rgba(54, 162, 235, 0.6)', 'rgba(75, 192, 192, 0.6)'],
      },
    ],
  };
  
  const intentData = {
    labels: Object.keys(messageStats.intentDistribution),
    datasets: [
      {
        label: 'Intent Distribution',
        data: Object.values(messageStats.intentDistribution),
        backgroundColor: [
          'rgba(255, 99, 132, 0.6)',
          'rgba(54, 162, 235, 0.6)',
          'rgba(255, 206, 86, 0.6)',
          'rgba(75, 192, 192, 0.6)',
          'rgba(153, 102, 255, 0.6)',
        ],
        borderColor: [
          'rgba(255, 99, 132, 1)',
          'rgba(54, 162, 235, 1)',
          'rgba(255, 206, 86, 1)',
          'rgba(75, 192, 192, 1)',
          'rgba(153, 102, 255, 1)',
        ],
        borderWidth: 1,
      },
    ],
  };

  return (
    <div className="analytics-container">
      <h2>Conversation Analytics</h2>
      
      <div className="analytics-grid">
        <div className="analytics-card">
          <h3>Message Statistics</h3>
          <p>User Messages: {messageStats.userCount}</p>
          <p>Bot Responses: {messageStats.botCount}</p>
          <p>Avg Response Time: {messageStats.avgResponseTime}ms</p>
          <div className="chart-container">
            <Bar 
              data={messageCountData} 
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'top' },
                  title: { display: true, text: 'Message Distribution' }
                }
              }} 
            />
          </div>
        </div>
        
        <div className="analytics-card">
          <h3>Intent Distribution</h3>
          <div className="chart-container">
            <Pie 
              data={intentData}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'right' },
                  title: { display: true, text: 'Intent Types' }
                }
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
