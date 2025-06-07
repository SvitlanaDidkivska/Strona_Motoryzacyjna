document.addEventListener('DOMContentLoaded', () => {
    const emojiPickerBtn = document.getElementById('emoji-picker-btn');
    const emojiPicker = document.getElementById('emoji-picker');
    const textarea = document.getElementById('id_content');
    const imageUploadInput = document.getElementById('image-upload');
    const imageUploadBtn = document.getElementById('image-upload-btn');
    const imagePreview = document.getElementById('image-preview');

    // List of emojis to show in picker
    const emojis = ['😀','😃','😄','😁','😆','😅','😂','🤣','😊','😇','🙂','🙃','😉','😌','😍','🥰','😘','😗','😙','😚','😋','😛','😝','😜','🤪','🤨','🧐','🤓','😎','🥳','😏','😒','😞','😔','😟','😕','🙁','☹️','😣','😖','😫','😩','🥺','😢','😭','😤','😠','😡','🤬','🤯','😳','🥵','🥶','😱','😨','😰','😥','😓','🤗','🤔','🤭','🤫','🤥','😶','😐','😑','😬','🙄','😯','😦','😧','😮','😲','🥱','😴','🤤','😪','😵','🤐','🥴','🤢','🤮','🤧','😷','🤒','🤕','🤑','🤠','😈','👿','👹','👺','🤡','💩','👻','💀','☠️','👽','👾','🤖'];

    // Populate emoji picker
    emojis.forEach(emoji => {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'emoji-btn text-lg p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded';
        btn.textContent = emoji;
        btn.addEventListener('click', () => {
            insertAtCursor(textarea, emoji);
            emojiPicker.classList.add('hidden');
        });
        emojiPicker.appendChild(btn);
    });

    emojiPickerBtn.addEventListener('click', () => {
        emojiPicker.classList.toggle('hidden');
    });

    // Insert emoji at cursor position in textarea
    function insertAtCursor(myField, myValue) {
        if (document.selection) {
            myField.focus();
            const sel = document.selection.createRange();
            sel.text = myValue;
            myField.focus();
        } else if (myField.selectionStart || myField.selectionStart === 0) {
            const startPos = myField.selectionStart;
            const endPos = myField.selectionEnd;
            const beforeValue = myField.value.substring(0, startPos);
            const afterValue = myField.value.substring(endPos, myField.value.length);
            myField.value = beforeValue + myValue + afterValue;
            myField.selectionStart = startPos + myValue.length;
            myField.selectionEnd = startPos + myValue.length;
            myField.focus();
        } else {
            myField.value += myValue;
            myField.focus();
        }
    }

    // Image upload button to trigger file input
    if (imageUploadBtn && imageUploadInput) {
        imageUploadBtn.addEventListener('click', () => {
            imageUploadInput.click();
        });

        // Handle image upload preview
        imageUploadInput.addEventListener('change', () => {
            const file = imageUploadInput.files[0];
            if (file) {
                // Clear previous preview
                imagePreview.innerHTML = '';

                // Create image element for preview
                const img = document.createElement('img');
                img.src = URL.createObjectURL(file);
                img.className = 'max-w-xs rounded-md shadow-md';
                img.onload = () => {
                    URL.revokeObjectURL(img.src); // Free memory
                };

                imagePreview.appendChild(img);
            }
        });
    }

    // Reaction buttons event handler
    document.querySelectorAll('.reaction-btn').forEach(button => {
        button.addEventListener('click', () => {
            const postId = button.getAttribute('data-post-id');
            const reactionType = button.getAttribute('data-reaction-type');

            fetch(`/forum/post/${postId}/reaction/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `reaction_type=${reactionType}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'added') {
                    button.classList.add('bg-blue-500', 'text-white');
                } else if (data.status === 'removed') {
                    button.classList.remove('bg-blue-500', 'text-white');
                }
            });
        });
    });

    // Helper to get CSRF token cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
