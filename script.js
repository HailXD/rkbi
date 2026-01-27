document.addEventListener('DOMContentLoaded', () => {
    const uploadBox = document.getElementById('uploadBox');
    const fileInput = document.getElementById('fileInput');
    const previewImage = document.getElementById('previewImage');
    const uploadText = document.getElementById('uploadText');

    const outputContainers = {
        'portfolio': document.getElementById('outputBox1Container'),
        'order': document.getElementById('outputBox2Container'),
        'order_o': document.getElementById('outputBox3Container'),
        'order_c': document.getElementById('outputBox4Container'),
        'order_op': document.getElementById('outputBox5Container'),
        'order_oc': document.getElementById('outputBox6Container')
    };

    const outputImages = {
        'portfolio': document.getElementById('outputImage1'),
        'order': document.getElementById('outputImage2'),
        'order_o': document.getElementById('outputImage3'),
        'order_c': document.getElementById('outputImage4'),
        'order_op': document.getElementById('outputImage5'),
        'order_oc': document.getElementById('outputImage6')
    };

    const downloadLinks = {
        'portfolio': document.getElementById('downloadLink1'),
        'order': document.getElementById('downloadLink2'),
        'order_o': document.getElementById('downloadLink3'),
        'order_c': document.getElementById('downloadLink4'),
        'order_op': document.getElementById('downloadLink5'),
        'order_oc': document.getElementById('downloadLink6')
    };

    const x = ((f) => f(f, Math.floor(Date.now() / 10)))((s, n) => n < 26 ? String.fromCharCode(97 + n % 26) : s(s, Math.floor(n / 26)) + String.fromCharCode(97 + n % 26));

    uploadBox.addEventListener('click', () => {
        fileInput.click();
    });

    fileInput.addEventListener('change', async (event) => {
        const file = event.target.files[0];
        if (!file) return;

        uploadText.style.display = 'none';
        previewImage.src = URL.createObjectURL(file);
        previewImage.style.display = 'block';

        const processTypes = ['portfolio', 'order', 'order_o', 'order_c', 'order_op', 'order_oc'];
        
        for (const type of processTypes) {
            const container = outputContainers[type];
            const outputImage = outputImages[type];
            
            container.style.display = 'flex';
            outputImage.style.display = 'none';
            
            const existingLoader = container.querySelector('.loader');
            if(existingLoader) existingLoader.remove();

            container.insertAdjacentHTML('beforeend', `<p class="loader" id="loader_${type}">Processing ${type.replace('_', ' ').toUpperCase()}...</p>`);
        }

        try {
            const promises = processTypes.map(type => {
                const formData = new FormData();
                formData.append('image', file);

                return fetch(`/process/${type}`, {
                    method: 'POST',
                    body: formData
                })
                .then(response => {
                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }
                    return response.json();
                })
                .then(data => ({ type, data }));
            });

            const results = await Promise.all(promises);

            for (const result of results) {
                const { type, data } = result;
                const loader = document.getElementById(`loader_${type}`);
                if (loader) loader.remove();

                const imageUrl = 'data:image/png;base64,' + data.image;
                outputImages[type].src = imageUrl;
                outputImages[type].style.display = 'block';
                downloadLinks[type].href = imageUrl;
                downloadLinks[type].download = `${x}_${type}.png`;
            }

        } catch (error) {
            console.error("Processing error:", error);
            uploadText.textContent = 'Error processing image.';
            uploadText.style.display = 'block';
            previewImage.style.display = 'none';
            
            for (const type of processTypes) {
                const loader = document.getElementById(`loader_${type}`);
                if (loader) loader.textContent = 'Error';
            }
        }
    });
});