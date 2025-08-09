import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { TrendingUp, TrendingDown } from "lucide-react";

interface TrendCardProps {
  title: string;
  value: number;
  change: number;
  unit?: string;
}

export function TrendCard({ title, value, change, unit = "" }: TrendCardProps) {
  const isPositive = change > 0;
  
  return (
    <Card>
      <CardHeader className="pb-1">
        <CardTitle className="text-xs font-medium text-muted-foreground">{title}</CardTitle>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="flex items-center justify-between">
          <div>
            <div className="text-lg font-bold">{value}{unit}</div>
            <div className={`flex items-center text-xs ${isPositive ? 'text-success' : 'text-destructive'}`}>
              {isPositive ? <TrendingUp className="w-3 h-3 mr-1" /> : <TrendingDown className="w-3 h-3 mr-1" />}
              {Math.abs(change)}%
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}