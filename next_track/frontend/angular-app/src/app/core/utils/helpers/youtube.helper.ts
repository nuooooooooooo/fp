export function getYoutubeWatchUrl(youtubeId: string): string {
  return `https://www.youtube.com/watch?v=${youtubeId}`;
}

export function getYoutubeEmbedUrl(
  youtubeId: string,
  origin?: string,
  autoplay = false
): string {
  const videoId = youtubeId.trim();
  const query = new URLSearchParams({
    rel: '0',
    modestbranding: '1',
    playsinline: '1',
    enablejsapi: '1',
    autoplay: autoplay ? '1' : '0',
  });

  if (origin) {
    query.set('origin', origin);
  }

  return `https://www.youtube-nocookie.com/embed/${videoId}?${query.toString()}`;
}
