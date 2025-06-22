import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import { submitFeedback } from './analyticsService';

const Feedback = ({ sessionId, onClose }) => {
  const { t } = useTranslation();
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async () => {
    if (!rating && !comment) return;
    await submitFeedback({
      session_id: sessionId,
      rating,
      comment,
      created_at: new Date().toISOString(),
    });
    setSubmitted(true);
    setTimeout(onClose, 800); // auto-close after brief "thank you"
  };

  if (submitted) {
    return (
      <div className="feedback-modal">
        <p>{t('feedback.thankYou')}</p>
      </div>
    );
  }

  return (
    <div className="feedback-modal" role="dialog" aria-labelledby="feedback-title">
      <h3 id="feedback-title">{t('feedback.title')}</h3>
      <div className="rating-group" aria-label={t('feedback.ratingLabel')}>
        {[1, 2, 3, 4, 5].map((n) => (
          <button
            key={n}
            className={`rating-star ${rating >= n ? 'selected' : ''}`}
            onClick={() => setRating(n)}
            aria-label={t('feedback.giveRating', { n })}
          >
            ★
          </button>
        ))}
      </div>
      <textarea
        value={comment}
        onChange={(e) => setComment(e.target.value)}
        placeholder={t('feedback.commentPlaceholder')}
        rows={3}
      />
      <div className="feedback-actions">
        <button onClick={handleSubmit} className="send-button">
          {t('feedback.submit')}
        </button>
        <button onClick={onClose} className="cancel-button">
          {t('feedback.cancel')}
        </button>
      </div>
    </div>
  );
};

export default Feedback;
