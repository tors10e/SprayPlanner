import React from 'react';

const FacebookFeed = React.memo((props) => {
  React.useEffect(() => {
    const script = document.createElement('script');
    script.src = "https://connect.facebook.net/en_US/sdk.js#xfbml=1&version=v17.0&appId=213335435001274&autoLogAppEvents=1";
    script.async = true;

    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    }
  }, []);

  return (
    <React.Fragment>
      <div id="fb-root"></div>
      <div class="fb-page" data-href="https://www.facebook.com/TerraIncognitaVineyard" data-show-posts="true"
        data-width="380" data-height="500" data-small-header="false" data-adapt-container-width="true"
        data-hide-cover="false" data-show-facepile="false">
        <blockquote cite="https://www.facebook.com/TerraIncognitaVineyard" class="fb-xfbml-parse-ignore">
            <a href="https://www.facebook.com/TerraIncognitaVineyard">Terra Incognita Vineyard</a>
        </blockquote></div>
    </React.Fragment>
  );
});

export default FacebookFeed