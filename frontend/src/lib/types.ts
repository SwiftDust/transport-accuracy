export type Feed = {
  id: string;
  rt_url: string;
  feed_name?: string;
  provider_name?: string;
  location?: string;
};

export type Mode = "delay_seconds" | "on_time" | "on_time_percentage";
