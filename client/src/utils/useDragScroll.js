import { useRef } from 'react'

export function useDragScroll() {
  const ref = useRef(null)
  const state = useRef({ isDown: false, startX: 0, scrollLeft: 0 })

  const onMouseDown = (e) => {
    const el = ref.current
    if (!el) return
    state.current.isDown = true
    state.current.startX = e.pageX - el.offsetLeft
    state.current.scrollLeft = el.scrollLeft
    el.classList.add('dragging')
  }

  const onMouseLeave = () => {
    state.current.isDown = false
    ref.current?.classList.remove('dragging')
  }

  const onMouseUp = () => {
    state.current.isDown = false
    ref.current?.classList.remove('dragging')
  }

  const onMouseMove = (e) => {
    const el = ref.current
    if (!state.current.isDown || !el) return
    e.preventDefault()
    const x = e.pageX - el.offsetLeft
    const walk = x - state.current.startX
    el.scrollLeft = state.current.scrollLeft - walk
  }

  return { ref, onMouseDown, onMouseLeave, onMouseUp, onMouseMove }
}
