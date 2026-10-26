let spinning = false;


async function spin() {

    if (spinning) {
        return;
    }

    spinning = true;

    const button =
        document.getElementById("spinButton");

    const reels = [
        document.getElementById("reel1"),
        document.getElementById("reel2"),
        document.getElementById("reel3")
    ];

    button.disabled = true;

    button.innerText = "SPINNING...";


    // Animasi
    const symbols = [
        "🍒",
        "🍋",
        "⭐",
        "💎",
        "7️⃣"
    ];


    for (let i = 0; i < 15; i++) {

        reels.forEach(reel => {

            reel.innerText =
                symbols[
                    Math.floor(
                        Math.random() * symbols.length
                    )
                ];

        });

        await sleep(60);
    }


    // Request ke Python
    const response =
        await fetch("/spin");

    const data =
        await response.json();


    // Jika error
    if (!response.ok) {

        document.getElementById("message")
            .innerText = data.error;

        button.disabled = false;

        button.innerText = "SPIN";

        spinning = false;

        return;
    }


    // Tampilkan hasil
    reels[0].innerText = data.result[0];

    reels[1].innerText = data.result[1];

    reels[2].innerText = data.result[2];


    // Update score
    document.getElementById("score")
        .innerText = data.total_score;


    // Update koin
    document.getElementById("coins")
        .innerText = data.coins;

    document.getElementById("coins-display")
        .innerText = data.coins;


    // Pesan
    document.getElementById("message")
        .innerText = data.message;


    button.disabled = false;

    button.innerText = "SPIN";

    spinning = false;
}


function sleep(ms) {

    return new Promise(
        resolve => setTimeout(resolve, ms)
    );

}