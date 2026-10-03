import React from 'react';
import Footer from '@theme-original/BlogPostItem/Footer';
import {useBlogPost} from '@docusaurus/plugin-content-blog/client';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

// Share links are plain URLs: no third-party scripts, no tracking pixels.
function ShareButtons({url, title}) {
  const u = encodeURIComponent(url);
  const t = encodeURIComponent(title);
  return (
    <div className="blog-share" aria-label="Share this post">
      <span className="blog-share__label">Share</span>
      <a
        className="blog-share__btn"
        href={`https://www.linkedin.com/sharing/share-offsite/?url=${u}`}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Share on LinkedIn">
        <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
          <path
            fill="currentColor"
            d="M20.45 20.45h-3.56v-5.57c0-1.33-.02-3.04-1.85-3.04-1.86 0-2.14 1.45-2.14 2.94v5.67H9.34V9h3.42v1.56h.05c.48-.9 1.64-1.85 3.37-1.85 3.6 0 4.27 2.37 4.27 5.46v6.28zM5.34 7.43a2.06 2.06 0 1 1 0-4.13 2.06 2.06 0 0 1 0 4.13zM7.12 20.45H3.56V9h3.56v11.45zM22.22 0H1.77C.79 0 0 .77 0 1.73v20.54C0 23.23.79 24 1.77 24h20.45c.98 0 1.78-.77 1.78-1.73V1.73C24 .77 23.2 0 22.22 0z"
          />
        </svg>
        LinkedIn
      </a>
      <a
        className="blog-share__btn"
        href={`https://twitter.com/intent/tweet?url=${u}&text=${t}`}
        target="_blank"
        rel="noopener noreferrer"
        aria-label="Share on X (Twitter)">
        <svg viewBox="0 0 24 24" width="16" height="16" aria-hidden="true">
          <path
            fill="currentColor"
            d="M18.24 2.25h3.31l-7.23 8.26 8.5 11.24h-6.66l-5.21-6.82-5.97 6.82H1.67l7.73-8.84L1.25 2.25h6.83l4.71 6.23 5.45-6.23zm-1.16 17.52h1.83L7.08 4.13H5.12l11.96 15.64z"
          />
        </svg>
        X (Twitter)
      </a>
    </div>
  );
}

export default function FooterWrapper(props) {
  const {metadata, isBlogPostPage} = useBlogPost();
  const {siteConfig} = useDocusaurusContext();
  return (
    <>
      <Footer {...props} />
      {isBlogPostPage && (
        <ShareButtons url={siteConfig.url + metadata.permalink} title={metadata.title} />
      )}
    </>
  );
}
