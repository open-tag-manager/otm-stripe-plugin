import PaymentInfo from './pages/PaymentInfo'

export default () => {
  return {
    router (config) {
      const orgRoute = config.routes.find(element => element.name === 'Org')
      const settingsRoute = orgRoute.children.find(element => element.name === 'Org-Settings')
      settingsRoute.children.push({
        path: 'payment',
        name: 'Org-Settings-Payment',
        component: PaymentInfo
      })
    },
    app (app) {
      app.$store.dispatch('addOrgMenu', {label: 'Payment Info', name: 'Org-Settings-Payment'})
    }
  }
}
