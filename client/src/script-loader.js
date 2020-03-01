let e = null
let isLoaded = false

export const loadStripeCheckout = () => {
  return new Promise((resolve) => {
    if (isLoaded) {
      resolve()
      return
    }

    if (e) {
      e.addEventListener('load', () => {
        resolve()
      })
      return
    }

    e = document.createElement('script')
    e.src = 'https://js.stripe.com/v3'
    document.getElementsByTagName('head')[0].appendChild(e)
    e.addEventListener('load', () => {
      isLoaded = true
      resolve()
    })
  })
}
