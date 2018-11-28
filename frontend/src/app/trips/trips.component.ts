import {Component, OnDestroy, OnInit} from '@angular/core';
import {Subscription} from 'rxjs/Subscription';
import {Trip} from './trip.model';
import {TripsApiService} from './trips-api.service';

@Component({
  selector: 'app-trips',
  templateUrl: './trips.component.html',

})
export class TripsComponent implements OnInit, OnDestroy {
  tripsListSubs: Subscription;
  tripsList: Trip[];

  constructor(private tripsApi: TripsApiService) {
  }

  ngOnInit() {
    this.tripsListSubs = this.tripsApi
      .getTrips()
      .subscribe(res => {
          this.tripsList = res;
        },
        console.error
      );
  }

  ngOnDestroy() {
    this.tripsListSubs.unsubscribe();
  }
}