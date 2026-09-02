import WidgetCode from './WidgetCode'
import ApiCode from './ApiCode'

export default function IntegrateTab({ apiKey }) {
  return (
    <div className="space-y-6">
   

      {/* Widget Code Section */}
      <WidgetCode apiKey={apiKey} />

      {/* API Code Section */}
      <ApiCode apiKey={apiKey} />
    </div>
  )
}