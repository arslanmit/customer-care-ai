import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
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
  const { t } = useTranslation();
  const [messageStats, setMessageStats] = useState({
    userCount: 0,
    botCount: 0,
    avgResponseTime: 0,
    intentDistribution: {}
  });

  useEffect(() => {
    if (!conversationHistory || conversationHistory.length === 0) return;
    
    try {
      // Calculate basic message statistics
      const userMessages = conversationHistory.filter(msg => msg.sender === 'user');
      const botMessages = conversationHistory.filter(msg => msg.sender === 'bot');
      
      // Extract intents from bot messages (or generate mock data if not available)
      const intentCounts = {};
      botMessages.forEach(msg => {
        if (msg.intent) {
          intentCounts[msg.intent] = (intentCounts[msg.intent] || 0) + 1;
        }
      });
      
      // If no real intents found, use mock data
      const mockIntents = Object.keys(intentCounts).length ? intentCounts : {
        'greet': Math.floor(Math.random() * 5) + 1,
        'ask_info': Math.floor(Math.random() * 5) + 1,
        'tell_joke': Math.floor(Math.random() * 5) + 1,
        'ask_time': Math.floor(Math.random() * 5) + 1,
        'goodbye': Math.floor(Math.random() * 5) + 1
      };
      
      // Calculate average response time (mock data for now)
      // In a real app, this would use timestamps from the messages
      const avgResponseTime = Math.floor(Math.random() * 500) + 200;
      
      // Update stats
      setMessageStats({
        userCount: userMessages.length,
        botCount: botMessages.length,
        avgResponseTime,
        intentDistribution: mockIntents
      });
    } catch (error) {
      console.error('Error analyzing conversation history:', error);
    }
  }, [conversationHistory]);

  const messageCountData = {
    labels: [t('analytics.userMessages'), t('analytics.botResponses')],
    datasets: [
      {
        label: t('analytics.messageStats'),
        data: [messageStats.userCount, messageStats.botCount],
        backgroundColor: ['rgba(54, 162, 235, 0.6)', 'rgba(75, 192, 192, 0.6)'],
        borderColor: ['rgba(54, 162, 235, 1)', 'rgba(75, 192, 192, 1)'],
        borderWidth: 1
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
    <div className="analytics-container" role="region" aria-labelledby="analytics-title">
      <h2 id="analytics-title">{t('analytics.title')}</h2>
      
      <div className="analytics-grid">
        <section className="analytics-card" aria-labelledby="message-stats-title">
          <h3 id="message-stats-title">{t('analytics.messageStats')}</h3>
          <div className="stats-summary">
            <p><strong>{t('analytics.userMessages')}:</strong> {messageStats.userCount}</p>
            <p><strong>{t('analytics.botResponses')}:</strong> {messageStats.botCount}</p>
            <p><strong>{t('analytics.avgResponseTime')}:</strong> {messageStats.avgResponseTime}ms</p>
          </div>
          <div className="chart-container" role="img" aria-label={t('analytics.messageDistribution')}>
            <Bar 
              data={messageCountData} 
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'top' },
                  title: { display: true, text: t('analytics.messageDistribution') }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    ticks: { precision: 0 }
                  }
                },
                maintainAspectRatio: false
              }} 
            />
          </div>
        </section>
        
        <section className="analytics-card" aria-labelledby="intent-dist-title">
          <h3 id="intent-dist-title">{t('analytics.intentDistribution')}</h3>
          <div className="chart-container" role="img" aria-label={t('analytics.intentDistribution')}>
            <Pie 
              data={intentData}
              options={{
                responsive: true,
                plugins: {
                  legend: { position: 'right' },
                  title: { display: true, text: t('analytics.intentTypes') },
                  tooltip: {
                    callbacks: {
                      label: (context) => {
                        const label = context.label || '';
                        const value = context.raw || 0;
                        const total = context.dataset.data.reduce((a, b) => a + b, 0);
                        const percentage = Math.round((value / total) * 100);
                        return `${label}: ${value} (${percentage}%)`;
                      }
                    }
                  }
                },
                maintainAspectRatio: false
              }}
            />
          </div>
        </section>
      </div>
    </div>
  );
};

export default Analytics;
