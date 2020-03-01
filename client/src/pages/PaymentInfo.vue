<template>
  <div class="container py-2">
    <h3>Payment Info</h3>

    <div v-if="inputCardInfo">
      <table>
        <tbody>
        <tr>
          <th>Name</th>
          <td>{{paymentData.name}}</td>
        </tr>
        <tr>
          <th>Email</th>
          <td>{{paymentData.email}}</td>
        </tr>
        <tr>
          <th>CardNumber</th>
          <td>xxxx-xxxx-xxxx-{{paymentData.payment_method.card.last4}} (Expires: {{paymentData.payment_method.card.exp_month}}/{{paymentData.payment_method.card.exp_year}})</td>
        </tr>
        </tbody>
        <button type="button" @click="activateCardForm" class="btn btn-primary my-4">Update Payment Info</button>
      </table>
    </div>
    <form @submit.prevent="submit" v-else>
      <div class="form-group">
        <label>Name</label>
        <input type="text" required v-model="name" class="form-control">
      </div>
      <div class="form-group">
        <label>Email</label>
        <input type="text" required v-model="email" class="form-control">
      </div>
      <div id="card-element"/>
      <button type="submit" class="btn btn-primary my-4">Submit</button>
    </form>

    <a href="https://stripe.com" target="_blank" rel="noopener">
      <img :src="stripeLogo" alt="Powered by Stripe"  />
    </a>
  </div>
</template>

<script>
  import stripeLogo from './powered_by_stripe.png'
  import {loadStripeCheckout} from "../script-loader"

  export default {
    data() {
      return {
        inputCardInfo: false,
        stripe: null,
        element: null,
        card: null,
        email: '',
        name: '',
        paymentData: null,
        stripeLogo
      }
    },
    async mounted() {
      const paymentData = await this.getPaymentInfo()
      if (paymentData) {
        this.inputCardInfo = true
        this.name = paymentData.name
        this.email = paymentData.email
        this.paymentData = paymentData
      } else {
        await this.activateCardForm()
      }
    },
    methods: {
      async submit() {
        const response = await this.stripe.createPaymentMethod({type: 'card', card: this.card, billing_details: {name: this.name, email: this.email}})
        const data = await this.$Amplify.API.put('OTMClientAPI', `/orgs/${this.$route.params.org}/payments`, {body: {
          name: this.name,
          email: this.email,
          payment_method: response.paymentMethod.id
        }})
        this.paymentData = data
        this.inputCardInfo = true
      },
      async getPaymentInfo () {
        const data = await this.$Amplify.API.get('OTMClientAPI', `/orgs/${this.$route.params.org}/payments`)
        return data
      },
      async activateCardForm () {
        this.inputCardInfo = false
        await this.$nextTick()
        await loadStripeCheckout()
        const stripe = window.Stripe(process.env.STRIPE_PK)
        const element = stripe.elements()
        const card = element.create('card')
        card.mount('#card-element')
        this.stripe = stripe
        this.element = element
        this.card = card
      }
    }
  }
</script>

<style scoped>
  .StripeElement {
    box-sizing: border-box;

    height: 40px;

    padding: 10px 12px;

    border: 1px solid transparent;
    border-radius: 4px;
    background-color: white;

    box-shadow: 0 1px 3px 0 #e6ebf1;
    -webkit-transition: box-shadow 150ms ease;
    transition: box-shadow 150ms ease;
  }

  .StripeElement--focus {
    box-shadow: 0 1px 3px 0 #cfd7df;
  }

  .StripeElement--invalid {
    border-color: #fa755a;
  }

  .StripeElement--webkit-autofill {
    background-color: #fefde5 !important;
  }
</style>
