<script>
    import logo from "$lib/assets/logo.png";
    import { getCountryDelays } from "$lib/api";

    let country = $state();
</script>

<div class="m-4">
    <div
        class="items-center md:items-start justify-center md:justify-start flex flex-row gap-6"
    >
        <img src={logo} alt="logo" />
        <div class="hidden md:flex md:flex-col">
            <p class="font-display text-2xl">
                <span class="font-bold text-primary">2,350</span>
                minutes of data logged and counting • Serving data of
                <span class="font-bold text-primary">172</span>
                unique providers
            </p>
            <p class="font-mono text-sm italic">
                made by <a
                    href="https://m4rt.nl"
                    class="text-gray-500 underline"
                >
                    m4rt.nl
                </a>
            </p>
        </div>
    </div>
    <div class="mt-30">
        <p class="text-5xl font-serif">
            I want to see <br />
            real-time<span class="align-super text-sm">*</span> data <br />
            of
            <input
                class="underline italic text-primary"
                placeholder="Netherlands"
                bind:value={country}
                oninput={async () => {
                    let delays = await getCountryDelays(country);
                    console.log(delays);
                }}
            />
        </p>
    </div>
    <div class="mt-5">
        <p class="text-sm font-display text-gray-500">
            * Realtime GTFS data may be less accurate or nonexistent in places.
        </p>
    </div>
    <div class="flex flex-col md:flex-row mt-10 gap-10">
        <div class="flex flex-col max-w-xs">
            <p class="text-green-600 font-display font-bold text-5xl">40.7</p>
            <p class="italic font-serif">seconds average delay right now</p>
            <hr class="my-2 h-0.5 border-t-0 bg-gray-400" />
            <p class="font-serif text-md">
                Not a bad score for 5:34PM, rush hour! That's less than a minute
                for the most crowded part of the day!
            </p>
        </div>
        <div class="flex flex-col max-w-xs">
            <p class="text-green-600 font-display font-bold text-5xl">5421</p>
            <p class="italic font-serif">trains on time</p>
            <hr class="my-2 h-0.5 border-t-0 bg-gray-400" />
            <p class="font-serif text-md">
                In your country, there's an average of 324 people on a train.
                This means 1.8 million people are transported to their
                destination without friction right now!
            </p>
        </div>
        <div class="flex flex-col max-w-xs">
            <p class="text-orange-600 font-display font-bold text-5xl">33.1%</p>
            <p class="italic font-serif">of trains aren't delayed right now</p>
            <hr class="my-2 h-0.5 border-t-0 bg-gray-400" />
            <p class="font-serif text-md">
                Even for rush hour, this is not the best ever, but keep in mind
                most of these are small &lt;5 minute delays.
            </p>
        </div>
    </div>
</div>
