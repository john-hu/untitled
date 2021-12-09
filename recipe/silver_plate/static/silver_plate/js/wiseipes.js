const onSearch = () => {
  if (!gtag) {
    return;
  }
  const keyword = document.querySelector('input[name=q]').value;
  gtag('event', 'search', { keyword: keyword });
};

const onRecipeClick = () => {
  if (!gtag) {
    return;
  }
  gtag('event', 'recipe_click', { href: event.currentTarget.href });
};
