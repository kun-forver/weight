/**
 * API client for uni-app (replaces axios)
 * Wraps uni.request with interceptors and Promise interface
 */

const BASE_URL = 'https://yoyo678.cc.cd/api'

function getToken() {
  return uni.getStorageSync('access_token') || ''
}

function setAuth(token, user) {
  uni.setStorageSync('access_token', token)
  uni.setStorageSync('user', JSON.stringify(user))
}

function clearAuth() {
  uni.removeStorageSync('access_token')
  uni.removeStorageSync('user')
}

function redirectToLogin() {
  const pages = getCurrentPages()
  const currentPath = pages.length > 0 ? pages[pages.length - 1].route : ''
  if (currentPath !== 'pages/login/index' && currentPath !== 'pages/register/index') {
    uni.reLaunch({ url: '/pages/login/index' })
  }
}

function request(config) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    const header = {
      'Content-Type': 'application/json',
      ...config.headers,
    }
    if (token) {
      header.Authorization = `Bearer ${token}`
    }

    uni.request({
      url: config.url.startsWith('http') ? config.url : BASE_URL + config.url,
      method: (config.method || 'GET').toUpperCase(),
      data: config.data,
      header,
      timeout: config.timeout || 15000,
      success(res) {
        if (res.statusCode === 401) {
          clearAuth()
          redirectToLogin()
          reject({ response: { status: 401, data: res.data } })
          return
        }
        if (res.statusCode >= 400) {
          reject({ response: { status: res.statusCode, data: res.data } })
          return
        }
        resolve({ data: res.data, status: res.statusCode })
      },
      fail(err) {
        reject({ message: err.errMsg || '网络请求失败' })
      },
    })
  })
}

/**
 * Upload file via uni.uploadFile (replaces FormData + axios.post)
 * @param {string} url - API path (relative to BASE_URL)
 * @param {string} filePath - local temp file path from uni.chooseImage
 * @param {string} name - field name for the file (default: 'file')
 * @param {object} formData - additional form data
 */
function uploadFile(url, filePath, name = 'file', formData = {}) {
  return new Promise((resolve, reject) => {
    const token = getToken()
    uni.uploadFile({
      url: BASE_URL + url,
      filePath,
      name,
      formData,
      header: {
        Authorization: token ? `Bearer ${token}` : '',
      },
      success(res) {
        let data
        try {
          data = JSON.parse(res.data)
        } catch (e) {
          data = res.data
        }
        if (res.statusCode >= 400) {
          reject({ response: { status: res.statusCode, data } })
          return
        }
        resolve({ data, status: res.statusCode })
      },
      fail(err) {
        reject({ message: err.errMsg || '上传失败' })
      },
    })
  })
}

export default {
  get(url, config = {}) {
    return request({ ...config, method: 'GET', url })
  },
  post(url, data, config = {}) {
    return request({ ...config, method: 'POST', url, data })
  },
  put(url, data, config = {}) {
    return request({ ...config, method: 'PUT', url, data })
  },
  delete(url, config = {}) {
    return request({ ...config, method: 'DELETE', url })
  },
  upload(url, filePath, name, formData) {
    return uploadFile(url, filePath, name, formData)
  },
}

export { setAuth, clearAuth, redirectToLogin }
