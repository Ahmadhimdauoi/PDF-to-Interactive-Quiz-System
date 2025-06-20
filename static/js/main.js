document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle course quiz submission
    const quizForms = document.querySelectorAll('#quizForm');
    quizForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData();
            const courseId = this.dataset.courseId;
            
            // Get all answers
            const questions = document.querySelectorAll('.question-card');
            questions.forEach((question, index) => {
                const answer = question.querySelector('input[type="radio"]:checked');
                if (answer) {
                    formData.append(`answer${index}`, answer.value);
                }
            });

            // Add course ID
            formData.append('course_id', courseId);

            // Send to server
            fetch('/submit-quiz', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    window.location.href = '/student';
                } else {
                    alert('حدث خطأ أثناء إرسال الإجابات');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('حدث خطأ أثناء إرسال الإجابات');
            });
        });
    });

    // Handle file upload
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'لا يوجد ملف مختار';
            this.nextElementSibling.textContent = fileName;
        });
    });
});
