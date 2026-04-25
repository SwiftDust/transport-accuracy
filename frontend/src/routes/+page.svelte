<script lang="ts">
    import logo from "$lib/assets/logo.png";
    import { getDelays, search, getAIAnalysis } from "$lib/api";
    import type { Mode } from "$lib/types";
    import countries from "i18n-iso-countries";
    import enLocale from "i18n-iso-countries/langs/en.json" assert { type: "json" };
    import "flag-icons/css/flag-icons.min.css";
    let { code } = $props();

    let query = $state("");
    let results: any = $state([]);
    let selected = $state(null);
    let open = $state(false);

    countries.registerLocale(enLocale);

    let averageDelay = $state("No data available");
    let trainsOnTime = $state("No data available");
    let onTimePercentage = $state("No data available");

    async function complete(q: string) {
        if (q.length < 2) {
            results = [];
            return;
        }
        results = await search(q);
        open = results.length > 0;
    }

    function select(feed: any) {
        selected = feed;
        query = feed.feed_name;
        open = false;
    }

    async function updateStats(feed: any) {
        const delays = await getDelays(feed).then((data) => {
            averageDelay = data.realtime.avg_delay;
            trainsOnTime = data.realtime.on_time;
            onTimePercentage = data.realtime.on_time_percentage;
        });
    }

    let country = $state("");

    async function updateAnalysis(mode: Mode, data: string) {
        const analysis = await getAIAnalysis(mode, country, data);
        console.log(analysis);
        return analysis;
    }
</script>

<div class="m-4">
    <div
        class="items-center md:items-start justify-center md:justify-start flex flex-row gap-6"
    >
        <img src={logo} alt="logo" />
        <div class="hidden md:flex md:flex-col">
            <p class="font-display text-2xl">
                Serving data of over
                <span class="font-bold text-primary">6000</span>
                unique providers
                <span class="text-xs text-gray-500"
                    >(powered by Mobility Database)</span
                >
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
        <div class="text-5xl font-serif">
            I want to see <br />
            real-time<span class="align-super text-sm">*</span> data of
            <div
                class="relative"
                onfocusout={(e) => {
                    if (!e.currentTarget.contains(e.relatedTarget)) {
                        open = false;
                    }
                }}
            >
                <input
                    class="underline italic text-primary"
                    placeholder="Netherlands"
                    bind:value={query}
                    oninput={() => {
                        complete(query);
                    }}
                />
                {#if open}
                    <div
                        class="absolute z-10 bg-white border rounded shadow w-md mt-1"
                        role="listbox"
                    >
                        {#each results as feed}
                            <div
                                class="px-3 py-2 hover:bg-gray-100 cursor-pointer flex flex-col"
                                onmousedown={() => {
                                    select(feed);
                                    updateStats(feed);
                                    country = feed.location;
                                }}
                                onkeydown={(e) => {
                                    if (e.key === "Enter" || e.key === " ") {
                                        select(feed);
                                        updateStats(feed);
                                        country = feed.location;
                                    }
                                }}
                                role="option"
                                aria-selected={selected === feed}
                                tabindex="0"
                            >
                                <span class="font-medium ml-2 text-lg">
                                    {feed.provider_name}
                                    {#if feed.feed_name}
                                        ({feed.feed_name})
                                    {/if}
                                </span>
                                <span class="italic ml-2 text-xs">
                                    <span
                                        class="fi fi-{countries
                                            .getAlpha2Code(feed.location, 'en')
                                            ?.toLowerCase()} border-black rounded-xs drop-shadow-md"
                                    ></span>
                                    {feed.location}
                                </span>
                            </div>
                        {/each}
                    </div>
                {/if}
            </div>
        </div>
    </div>

    <div class="mt-5">
        <p class="text-sm font-display text-gray-500">
            * Realtime GTFS data may be less accurate or nonexistent in places.<br
            />
            How to use: Type in the full country or provider name and wait for the
            feeds to load (be patient, this may take up to 30 seconds due to API limitations).
            Then choose the data you want to see.
        </p>
    </div>
    {#if selected}
        <div class="flex flex-col md:flex-row mt-10 gap-10">
            <div class="flex flex-col max-w-xs">
                <p
                    class="{averageDelay < 60
                        ? 'text-green-600'
                        : averageDelay < 180
                          ? 'text-yellow-600'
                          : 'text-red-600'} font-display font-bold text-5xl"
                >
                    {Math.round(averageDelay * 10) / 10}
                </p>
                <p class="italic font-serif">seconds average delay right now</p>
                <hr class="my-2 h-0.5 border-t-0 bg-gray-400" />
                <div class="font-serif text-md">
                    {#await updateAnalysis("delay_seconds", (Math.round(averageDelay * 10) / 10).toString())}
                        <p>
                            AI analysis loading... please be patient as this may
                            take up to a couple of minutes
                        </p>
                    {:then result}
                        <p>{result}</p>
                    {:catch error}
                        <p>Error: {error.message}</p>
                    {/await}
                </div>
            </div>
            <div class="flex flex-col max-w-xs">
                <p class={`text-green-600 font-display font-bold text-5xl`}>
                    {trainsOnTime}
                </p>
                <p class="italic font-serif">trains on time</p>
                <hr class="my-2 h-0.5 border-t-0 bg-gray-400" />
                <div class="font-serif text-md">
                    {#await updateAnalysis("on_time", trainsOnTime.toString())}
                        <p>
                            AI analysis loading... please be patient as this may
                            take up to a couple of minutes
                        </p>
                    {:then result}
                        <p>{result}</p>
                    {:catch error}
                        <p>Error: {error.message}</p>
                    {/await}
                </div>
            </div>
            <div class="flex flex-col max-w-xs">
                <p
                    class={`${
                        onTimePercentage >= 75
                            ? "text-green-600"
                            : onTimePercentage >= 35
                              ? "text-yellow-600"
                              : "text-red-600"
                    } font-display font-bold text-5xl`}
                >
                    {Math.round(onTimePercentage * 10) / 10}%
                </p>
                <p class="italic font-serif">
                    of trains aren't delayed right now
                </p>
                <hr class="my-2 h-0.5 border-t-0 bg-gray-400" />
                <div class="font-serif text-md">
                    {#await updateAnalysis("on_time_percentage", onTimePercentage.toString())}
                        <p>
                            AI analysis loading... please be patient as this may
                            take up to a couple of minutes
                        </p>
                    {:then result}
                        <p>{result}</p>
                    {:catch error}
                        <p>Error: {error.message}</p>
                    {/await}
                </div>
            </div>
        </div>
    {/if}
</div>
