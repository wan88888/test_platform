import axios from 'axios'

// OAuth must also work when the browser has an expired TestHub JWT.
// This client intentionally has no JWT refresh/logout interceptors.
export default axios.create({ baseURL: '/api/auth/feishu', timeout: 30000 })
