import { Component, OnInit } from '@angular/core';
import { VehicleStatus, VehicleType } from '../../shared/constants/enums';
import { Vehicle } from '../../shared/models/vehicle.model';
import { ApiService } from '../../shared/services/api.service';

@Component({ standalone: false,
  template: `<section class="page">
  <h1>车辆管理</h1>
  <div class="toolbar">
    <mat-form-field>
      <mat-label>类型</mat-label>
      <mat-select [(ngModel)]="type" (selectionChange)="load()">
        <mat-option value="">全部</mat-option>
        <mat-option *ngFor="let t of vehicleTypes" [value]="t">{{ t }}</mat-option>
      </mat-select>
    </mat-form-field>
    <mat-form-field>
      <mat-label>状态</mat-label>
      <mat-select [(ngModel)]="status" (selectionChange)="load()">
        <mat-option value="">全部</mat-option>
        <mat-option *ngFor="let s of statuses" [value]="s">{{ s | statusTranslate }}</mat-option>
      </mat-select>
    </mat-form-field>
    <mat-form-field>
      <mat-label>保险到期</mat-label>
      <mat-select [(ngModel)]="insuranceStatus" (selectionChange)="load()">
        <mat-option value="">全部</mat-option>
        <mat-option value="expired">已过期</mat-option>
        <mat-option value="expiring_7">7天内到期</mat-option>
        <mat-option value="expiring_30">30天内到期</mat-option>
        <mat-option value="expiring_90">90天内到期</mat-option>
      </mat-select>
    </mat-form-field>
    <button mat-flat-button color="primary" *appHasRole="['OPERATOR','ADMIN']">注册车辆</button>
  </div>
  <div class="table-wrap">
    <table>
      <thead>
        <tr>
          <th>车牌</th>
          <th>类型</th>
          <th>车型</th>
          <th>司机</th>
          <th>保险到期</th>
          <th>状态</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr *ngFor="let v of vehicles" [class.row-warning]="v.insurance_days_remaining >= 0 && v.insurance_days_remaining <= 30" [class.row-danger]="v.insurance_days_remaining < 0">
          <td><a [routerLink]="['/vehicles', v.id]">{{ v.plate_number }}</a></td>
          <td>{{ v.type }}</td>
          <td>{{ v.brand }} {{ v.model }}</td>
          <td>{{ v.driver_detail?.username || '-' }}</td>
          <td>
            <span [class.text-danger]="v.insurance_days_remaining < 0" [class.text-warning]="v.insurance_days_remaining >= 0 && v.insurance_days_remaining <= 30">
              {{ v.insurance_expiry }}
              <small class="days-badge" *ngIf="v.insurance_days_remaining < 0">已过期{{ -v.insurance_days_remaining }}天</small>
              <small class="days-badge days-warning" *ngIf="v.insurance_days_remaining >= 0 && v.insurance_days_remaining <= 30">剩{{ v.insurance_days_remaining }}天</small>
            </span>
          </td>
          <td><app-status-tag [value]="v.status"></app-status-tag></td>
          <td><button mat-button *appHasRole="['OPERATOR','ADMIN']">审核/调度</button></td>
        </tr>
      </tbody>
    </table>
  </div>
</section>`,
  styles: [
    `
    .row-danger { background-color: #fff1f0; }
    .row-warning { background-color: #fffbe6; }
    .text-danger { color: #d4380d; font-weight: 600; }
    .text-warning { color: #d48806; font-weight: 600; }
    .days-badge {
      display: inline-block;
      margin-left: 6px;
      padding: 1px 6px;
      font-size: 11px;
      border-radius: 10px;
      background: #fff1f0;
      color: #d4380d;
    }
    .days-badge.days-warning {
      background: #fffbe6;
      color: #d48806;
    }
    `
  ]
})
export class VehicleListComponent implements OnInit {
  vehicles: Vehicle[] = [];
  type = '';
  status = '';
  insuranceStatus = '';
  vehicleTypes = Object.values(VehicleType);
  statuses = Object.values(VehicleStatus);
  constructor(private api: ApiService) {}
  ngOnInit(): void { this.load(); }
  load(): void {
    const filters: Record<string, string> = { type: this.type, status: this.status };
    if (this.insuranceStatus) {
      filters['insurance_status'] = this.insuranceStatus;
    }
    this.api.listVehicles(filters).subscribe(v => this.vehicles = v);
  }
}
