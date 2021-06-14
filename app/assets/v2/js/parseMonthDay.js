// convert round dates to expected format
const parseMonthDay = (given) => {
  // parse date
  const date = new Date(parseInt(given) * 1000);

  // parse day/month (feed undefined to get local version)
  const day = date.toLocaleDateString(undefined, {'day': 'numeric'});
  const month = date.toLocaleDateString(undefined, {'month': 'long'});

  // return required format
  return `${month} ${day}`;
};
