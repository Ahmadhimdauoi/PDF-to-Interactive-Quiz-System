import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const StudentDashboard = () => {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  const [score, setScore] = useState(0);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      const response = await fetch('/api/courses');
      const data = await response.json();
      setCourses(data.courses);
    } catch (error) {
      console.error('Error fetching courses:', error);
    }
  };

  const fetchQuestions = async (courseId) => {
    try {
      const response = await fetch(`/api/course/${courseId}/questions`);
      const data = await response.json();
      setQuestions(data.questions);
      setAnswers({});
      setShowResults(false);
      setScore(0);
    } catch (error) {
      console.error('Error fetching questions:', error);
    }
  };

  const handleAnswer = (questionId, answer) => {
    setAnswers(prevAnswers => ({
      ...prevAnswers,
      [questionId]: answer
    }));
  };

  const submitQuiz = async () => {
    try {
      const response = await fetch('/api/submit-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          courseId: selectedCourse,
          answers: answers,
        }),
      });
      const data = await response.json();
      setScore(data.score);
      setShowResults(true);
    } catch (error) {
      console.error('Error submitting quiz:', error);
    }
  };

  const renderQuestion = (question, index) => {
    const questionType = question.type;
    const answer = answers[question.id];

    switch (questionType) {
      case 'mcq':
        return (
          <div key={question.id} className="mb-4">
            <h5>{index + 1}. {question.text}</h5>
            {question.options.map((option, i) => (
              <div key={i} className="form-check">
                <input
                  className="form-check-input"
                  type="radio"
                  name={`q${question.id}`}
                  value={option}
                  checked={answer === option}
                  onChange={() => handleAnswer(question.id, option)}
                />
                <label className="form-check-label">{option}</label>
              </div>
            ))}
          </div>
        );
      case 'tf':
        return (
          <div key={question.id} className="mb-4">
            <h5>{index + 1}. {question.text}</h5>
            <div className="form-check">
              <input
                className="form-check-input"
                type="radio"
                name={`q${question.id}`}
                value="true"
                checked={answer === 'true'}
                onChange={() => handleAnswer(question.id, 'true')}
              />
              <label className="form-check-label">صح</label>
            </div>
            <div className="form-check">
              <input
                className="form-check-input"
                type="radio"
                name={`q${question.id}`}
                value="false"
                checked={answer === 'false'}
                onChange={() => handleAnswer(question.id, 'false')}
              />
              <label className="form-check-label">خطأ</label>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="container mt-5">
      {!selectedCourse ? (
        <div>
          <h2>قائمة المواد المتاحة</h2>
          <div className="list-group mt-4">
            {courses.map(course => (
              <button
                key={course.id}
                className="list-group-item list-group-item-action"
                onClick={() => {
                  setSelectedCourse(course.id);
                  fetchQuestions(course.id);
                }}
              >
                {course.name}
              </button>
            ))}
          </div>
        </div>
      ) : (
        <div>
          <h2>{selectedCourse}</h2>
          <div className="mt-4">
            {showResults ? (
              <div>
                <h3>النتيجة: {score}%</h3>
                <button
                  className="btn btn-primary mt-3"
                  onClick={() => {
                    setSelectedCourse(null);
                  }}
                >
                  العودة إلى قائمة المواد
                </button>
              </div>
            ) : (
              <div>
                {questions.map((question, index) => renderQuestion(question, index))}
                <button
                  className="btn btn-primary mt-3"
                  onClick={submitQuiz}
                  disabled={Object.keys(answers).length !== questions.length}
                >
                  إرسال الاختبار
                </button>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StudentDashboard;
