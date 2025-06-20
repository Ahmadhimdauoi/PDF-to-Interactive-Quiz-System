import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const AdminDashboard = () => {
  const navigate = useNavigate();
  const [courseName, setCourseName] = useState('');
  const [numQuestions, setNumQuestions] = useState('');
  const [language, setLanguage] = useState('ar');
  const [questionType, setQuestionType] = useState('mcq');
  const [pdfFile, setPdfFile] = useState(null);
  const [additionalFiles, setAdditionalFiles] = useState([]);

  const handlePdfUpload = (e) => {
    setPdfFile(e.target.files[0]);
  };

  const handleAdditionalFileUpload = (e) => {
    const newFiles = [...additionalFiles, ...e.target.files];
    setAdditionalFiles(newFiles);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('courseName', courseName);
    formData.append('numQuestions', numQuestions);
    formData.append('language', language);
    formData.append('questionType', questionType);
    formData.append('pdfFile', pdfFile);

    // Add additional files
    additionalFiles.forEach((file, index) => {
      formData.append(`additionalFile${index}`, file);
    });

    try {
      const response = await fetch('/api/create-course', {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      if (data.success) {
        alert('تم إنشاء المادة بنجاح!');
        navigate('/admin');
      } else {
        alert('حدث خطأ أثناء إنشاء المادة');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('حدث خطأ أثناء إنشاء المادة');
    }
  };

  return (
    <div className="container mt-5">
      <h2>لوحة تحكم المشرف</h2>
      <form onSubmit={handleSubmit} className="mt-4">
        <div className="mb-3">
          <label className="form-label">اسم المادة</label>
          <input
            type="text"
            className="form-control"
            value={courseName}
            onChange={(e) => setCourseName(e.target.value)}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">عدد الأسئلة</label>
          <input
            type="number"
            className="form-control"
            value={numQuestions}
            onChange={(e) => setNumQuestions(e.target.value)}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">لغة الواجهة</label>
          <select
            className="form-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
            required
          >
            <option value="ar">العربية</option>
            <option value="en">الإنجليزية</option>
          </select>
        </div>

        <div className="mb-3">
          <label className="form-label">نوع الأسئلة</label>
          <select
            className="form-select"
            value={questionType}
            onChange={(e) => setQuestionType(e.target.value)}
            required
          >
            <option value="mcq">اختيار من متعدد</option>
            <option value="tf">صح/خطأ</option>
          </select>
        </div>

        <div className="mb-3">
          <label className="form-label">رفع ملف PDF</label>
          <input
            type="file"
            className="form-control"
            accept=".pdf"
            onChange={handlePdfUpload}
            required
          />
        </div>

        <div className="mb-3">
          <label className="form-label">رفع ملفات إضافية (اختياري)</label>
          <input
            type="file"
            className="form-control"
            accept=".pdf,.doc,.docx"
            multiple
            onChange={handleAdditionalFileUpload}
          />
        </div>

        <button type="submit" className="btn btn-primary">
          إنشاء المادة
        </button>
      </form>
    </div>
  );
};

export default AdminDashboard;
