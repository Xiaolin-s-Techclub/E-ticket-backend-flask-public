document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('form');
    const last_name = document.getElementById('last_name');
    const first_name = document.getElementById('first_name');
    const email = document.getElementById('email');
    const email_confirm = document.getElementById('email_confirm');
    // const grades = document.getElementById('school_grades');
    // const classes = document.getElementById('classes');
    // const student_number = document.getElementById('student_number');
    // const student_id = document.getElementById('学籍番号'); // HTMLと合わせる
    const ticketQuantity = document.getElementById('ticketQuantity'); // 修正
    const guestNames = document.getElementById('guestNameFormContainer');

    function showGuestNameForms() {
        var ticketQuantity = document.getElementById("ticketQuantity").value; // 修正
        var container = document.getElementById("guestNameFormContainer");
        container.innerHTML = "";

        for (var i = 1; i <= ticketQuantity; i++) {
            var label = document.createElement("label");
            label.setAttribute("for", "guestName" + i);
            label.textContent = "来場者" + i + "の氏名: - name of visitor 1"; // ラベルテキストを追加

            var input = document.createElement("input");
            input.setAttribute("type", "text");
            input.setAttribute("name", "guestName" + i);
            input.setAttribute("id", "guestName" + i);
            input.setAttribute("placeholder", "来場者" + i + "の氏名 - name");
            input.required = true;

            container.appendChild(label);
            container.appendChild(input);
            container.appendChild(document.createElement("br"));
        }
    }

    ticketQuantity.addEventListener('change', showGuestNameForms); // 修正

    function validateForm(e) {
        // const emailPattern = /@mita-is\.ed\.jp$/;
        // const studentNumberPattern = /^\d{7}$/;  // 半角数字のみを許可

        if (last_name.value === '' || last_name.value == null) {
            e.preventDefault();
            alert('姓を入力してください');
            last_name.focus();
            return false;
        } else if (first_name.value === '' || first_name.value == null) {
            e.preventDefault();
            alert('名を入力してください');
            first_name.focus();
            return false;
        } else if (email.value === '' || email.value == null) {
            e.preventDefault();
            alert('メールアドレスを入力してください');
            email.focus();
            return false;
        // } else if (!emailPattern.test(email.value)) {
        //     e.preventDefault();
        //     alert('メールアドレスは "********@mita-is.ed.jp" の形式で入力してください');
        //     email.focus();
        //     return false;
        } else if (email.value !== email_confirm.value) {
            e.preventDefault();
            alert('確認用メールアドレスが一致しません');
            email_confirm.focus();
            return false;
        // } else if (student_id.value === '' || student_id.value == null) {
        //     e.preventDefault();
        //     alert('学籍番号を入力してください');
        //     student_id.focus();
        //     return false;
        // } else if (!studentNumberPattern.test(student_id.value)) {
        //     e.preventDefault();
        //     alert('学籍番号は7桁の半角数字で入力してください');
        //     student_id.focus();
        //     return false;
        }

        return true;
    }

    form.addEventListener('submit', function (e) {
        validateForm(e);
    });

});
