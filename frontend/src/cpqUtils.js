export const validateRangeIncrement = (name, value, min, max, step) => {
    const numValue = parseFloat(value)
    const numMin = parseFloat(min)
    const numMax = parseFloat(max)
    const numStep = parseFloat(step)
  
    // Validate if the value is numeric
    if (!/^\d*\.?\d*$/.test(value)) return 'Invalid Input.'
  
    // Validate if the value is within min and max range
    if (numValue < numMin || numValue > numMax) return `Value should be between ${min} and ${max}`
  
    // // Handle decimal places for step validation
    // const stepDecimalPlaces = (step.toString().split('.')[1]?.length) || 0
    // const valueDecimalPlaces = (value.toString().includes('.') ? value.split('.')[1].length : 0) || 0
  
    // // Validate if the value follows the step increment
    // if (stepDecimalPlaces > 0) {
    //   if (numValue === numMin || numValue === numMax) return null
    //   if (valueDecimalPlaces !== stepDecimalPlaces) return `Value should increment by ${step}`
    // } else {
    //   if (value.toString().includes('.') && value.toString().split('.')[1].length === 0) return 'Invalid Input.'
    //   if ((numValue - numMin) % numStep !== 0) return `Value should increment by ${step}`
    // }

    // Validate if the value follows the step increment
  const diff = (numValue - numMin)
  const precision = Math.max((step.toString().split('.')[1]?.length) || 0, 6)
  const rounded = parseFloat((diff / numStep).toFixed(precision))

  if (Math.abs(rounded - Math.round(rounded)) > 1e-6) {
    return `Value should increment by ${step}`
  }
   // Disallow trailing decimal like "5."
   if (value.includes('.') && value.endsWith('.')) {
    return 'Invalid Input. Please enter digits after decimal point.'
  }
  
    return null
  }
  